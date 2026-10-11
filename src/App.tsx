import { useCallback, useEffect, useMemo, useRef, useState, type ReactElement } from 'react';
import { App as CapacitorApp } from '@capacitor/app';
import type { Program, Session, Settings, WorkoutRecord } from './types';
import { allPrograms, exerciseKey, findProgram } from './data/programs';
import { isNative, restTimer, saveJsonFile } from './native';
import { mergeHistory, storage, upsertRecord } from './storage';
import { createSession, lastWeights, migrateSession, reduce, restTimerText, toRecord, type Action } from './workout/engine';
import Home from './screens/Home';
import Preview from './screens/Preview';
import Active from './screens/Active';
import Complete from './screens/Complete';
import History from './screens/History';
import SettingsScreen from './screens/Settings';
import WeightDialog from './screens/WeightDialog';

type View =
  | { name: 'home' }
  | { name: 'preview'; dayId: string }
  | { name: 'active' }
  | { name: 'complete' }
  | { name: 'history' }
  | { name: 'historyDetail'; id: string }
  | { name: 'settings' };

export default function App() {
  const [imported, setImported] = useState<Program[]>(() => storage.loadPrograms());
  const programs = useMemo(() => allPrograms(imported), [imported]);
  const [session, setSession] = useState<Session | null>(() => migrateSession(storage.loadSession(), allPrograms(storage.loadPrograms())));
  const [history, setHistory] = useState<WorkoutRecord[]>(() => storage.loadHistory());
  const [restOverrides, setRestOverrides] = useState<Record<string, number>>(() => storage.loadRestOverrides());
  const [settings, setSettings] = useState<Settings>(() => storage.loadSettings());
  const [view, setView] = useState<View>({ name: 'home' });
  const [toast, setToast] = useState<string | null>(null);
  const program = findProgram(programs, settings.programId);

  // Everything that matters survives a refresh, a closed app or a dead battery.
  useEffect(() => {
    storage.saveSession(session);
  }, [session]);
  useEffect(() => {
    storage.saveHistory(history);
  }, [history]);
  useEffect(() => {
    storage.saveRestOverrides(restOverrides);
  }, [restOverrides]);
  useEffect(() => {
    storage.saveSettings(settings);
  }, [settings]);
  useEffect(() => {
    storage.savePrograms(imported);
  }, [imported]);
  useEffect(() => {
    if (!toast) return;
    const id = window.setTimeout(() => setToast(null), 2600);
    return () => window.clearTimeout(id);
  }, [toast]);

  // Each set goes straight into the history, so a workout is never lost by closing the app,
  // skipping the summary or starting another day.
  useEffect(() => {
    if (!session) return;
    const rec = toRecord(session);
    setHistory((h) => (rec.totalSetsDone > 0 ? upsertRecord(h, rec) : h.some((r) => r.id === rec.id) ? h.filter((r) => r.id !== rec.id) : h));
  }, [session]);

  const dispatch = useCallback((a: Action) => {
    setSession((s) => (s ? reduce(s, a) : s));
  }, []);
  const suggested = useMemo(() => lastWeights(history, session?.id), [history, session?.id]);

  // Android app: countdown in the notification shade and an alarm that rings even when the app is hidden.
  const timerKey = useRef('boot');
  useEffect(() => {
    const s = session;
    if (s && s.phase === 'RESTING' && s.restEndsAt && s.restTarget && s.restEndsAt > Date.now()) {
      const key = `${s.id}:${s.restEndsAt}:${settings.sound}:${settings.vibrate}`;
      if (timerKey.current === key) return;
      timerKey.current = key;
      restTimer.start({ endAt: s.restEndsAt, ...restTimerText(s), sound: settings.sound, vibrate: settings.vibrate });
    } else if (timerKey.current !== '') {
      timerKey.current = '';
      restTimer.cancel();
    }
  }, [session, settings.sound, settings.vibrate]);

  // The last set of the last exercise finishes the workout: show the summary.
  useEffect(() => {
    if (session?.phase === 'FINISHED' && view.name === 'active') setView({ name: 'complete' });
  }, [session?.phase, view.name]);
  useEffect(() => {
    if (!session && (view.name === 'active' || view.name === 'complete')) setView({ name: 'home' });
  }, [session, view.name]);

  const startWorkout = (dayId: string) => {
    const day = program.days.find((d) => d.id === dayId);
    if (!day) return;
    // A workout that is still open gets finished first; its sets are already in the history.
    if (session && session.phase !== 'FINISHED') {
      const rec = toRecord(reduce(session, { type: 'FINISH', now: Date.now() }));
      if (rec.totalSetsDone > 0) setHistory((h) => upsertRecord(h, rec));
    }
    restTimer.prepare();
    setSession(createSession(program, day, { restOverrides, now: Date.now() }));
    setView({ name: 'active' });
  };
  const closeSession = () => {
    setSession(null);
    setView({ name: 'home' });
  };
  const deleteRecord = (id: string) => {
    setHistory((h) => h.filter((r) => r.id !== id));
    if (session?.id === id) setSession(null);
    setToast('Treniruotė ištrinta');
  };
  const setRest = (key: string, seconds: number | null) =>
    setRestOverrides((o) => {
      const next = { ...o };
      if (seconds === null) delete next[key];
      else next[key] = seconds;
      return next;
    });

  const importProgram = (p: Program) => {
    setImported((list) => [...list.filter((x) => x.id !== p.id), p]);
    setSettings((s) => ({ ...s, programId: p.id }));
    setToast(`Programa „${p.programName}“ įkelta ir pasirinkta`);
  };
  const deleteProgram = (id: string) => {
    setImported((list) => list.filter((x) => x.id !== id));
    if (settings.programId === id) setSettings((s) => ({ ...s, programId: undefined }));
    setToast('Programa ištrinta');
  };
  const exportBackup = async () => {
    const data = JSON.stringify(
      { app: 'Kyokushin Training', version: 2, exportedAt: new Date().toISOString(), history, programs: imported, settings, restOverrides },
      null,
      2,
    );
    try {
      await saveJsonFile(`kyokushin-kopija-${new Date().toISOString().slice(0, 10)}.json`, data);
    } catch (e) {
      if (!/cancel/i.test(String((e as Error)?.message))) setToast('Nepavyko sukurti kopijos');
    }
  };
  const importBackup = (raw: unknown): string => {
    const d = raw as { history?: unknown; programs?: unknown };
    if (!d || typeof d !== 'object' || !Array.isArray(d.history)) throw new Error('Tai ne Kyokushin kopijos failas (nėra „history“).');
    const incoming = mergeHistory(d.history as WorkoutRecord[], []);
    setHistory((h) => mergeHistory(h, incoming));
    if (Array.isArray(d.programs)) {
      const ok: Program[] = [];
      for (const p of d.programs) if (p && typeof p === 'object' && Array.isArray((p as Program).days)) ok.push({ ...(p as Program), source: 'imported' });
      if (ok.length) setImported((list) => [...list.filter((x) => !ok.some((o) => o.id === x.id)), ...ok]);
    }
    return `Įkelta treniruočių: ${incoming.length}`;
  };

  // Android back button: one screen back instead of closing the app. A running workout is always saved.
  const live = useRef({ view, session });
  live.current = { view, session };
  useEffect(() => {
    if (!isNative) return;
    const handle = CapacitorApp.addListener('backButton', () => {
      const { view: v, session: s } = live.current;
      if (s?.pendingWeightFor && (v.name === 'active' || v.name === 'complete')) {
        dispatch({ type: 'RESOLVE_WEIGHT', exerciseId: s.pendingWeightFor, value: null });
        return;
      }
      if (v.name === 'home') {
        CapacitorApp.minimizeApp().catch(() => undefined);
        return;
      }
      if (v.name === 'historyDetail') {
        setView({ name: 'history' });
        return;
      }
      if (v.name === 'complete') {
        setSession(null);
        setView({ name: 'home' });
        return;
      }
      setView({ name: 'home' });
    });
    return () => {
      handle.then((h) => h.remove()).catch(() => undefined);
    };
  }, [dispatch]);

  let screen: ReactElement;
  switch (view.name) {
    case 'preview': {
      const day = program.days.find((d) => d.id === view.dayId);
      screen = day ? (
        <Preview
          program={program}
          day={day}
          restOverrides={restOverrides}
          onSetRest={setRest}
          onStart={() => startWorkout(day.id)}
          onBack={() => setView({ name: 'home' })}
          active={session}
        />
      ) : (
        <></>
      );
      break;
    }
    case 'active':
      screen = session ? <Active session={session} dispatch={dispatch} settings={settings} suggested={suggested} onExit={() => setView({ name: 'home' })} /> : <></>;
      break;
    case 'complete':
      screen = session ? (
        <Complete
          session={session}
          suggested={suggested}
          dispatch={dispatch}
          onClose={closeSession}
          onDelete={() => {
            deleteRecord(session.id);
            setView({ name: 'home' });
          }}
          onReopen={() => {
            dispatch({ type: 'REOPEN' });
            setView({ name: 'active' });
          }}
        />
      ) : (
        <></>
      );
      break;
    case 'history':
      screen = <History history={history} activeId={session?.id} onOpen={(id) => setView({ name: 'historyDetail', id })} onBack={() => setView({ name: 'home' })} />;
      break;
    case 'historyDetail':
      screen = (
        <History
          history={history}
          activeId={session?.id}
          detailId={view.id}
          onOpen={(id) => setView({ name: 'historyDetail', id })}
          onBack={() => setView({ name: 'history' })}
          onDelete={(id) => {
            deleteRecord(id);
            setView({ name: 'history' });
          }}
        />
      );
      break;
    case 'settings':
      screen = (
        <SettingsScreen
          programs={programs}
          program={program}
          settings={settings}
          historyCount={history.length}
          onSettings={setSettings}
          onSelectProgram={(id) => setSettings((s) => ({ ...s, programId: id }))}
          onImportProgram={importProgram}
          onDeleteProgram={deleteProgram}
          onExportBackup={exportBackup}
          onImportBackup={importBackup}
          onToast={setToast}
          onBack={() => setView({ name: 'home' })}
        />
      );
      break;
    default:
      screen = (
        <Home
          program={program}
          session={session}
          history={history}
          onPickDay={(d) => setView({ name: 'preview', dayId: d })}
          onResume={() => setView(session?.phase === 'FINISHED' ? { name: 'complete' } : { name: 'active' })}
          onFinishActive={() => {
            dispatch({ type: 'FINISH', now: Date.now() });
            setView({ name: 'complete' });
          }}
          onCloseFinished={closeSession}
          onHistory={() => setView({ name: 'history' })}
          onSettings={() => setView({ name: 'settings' })}
        />
      );
  }

  const pending =
    session?.pendingWeightFor && (view.name === 'active' || view.name === 'complete')
      ? session.day.exercises.findIndex((e) => e.id === session.pendingWeightFor)
      : -1;
  const pendingEx = session && pending >= 0 ? session.day.exercises[pending] : null;

  return (
    <>
      {screen}
      {session && pendingEx && (
        <WeightDialog
          key={session.id + pendingEx.id}
          exercise={pendingEx}
          color={session.day.color}
          setsDone={session.logs[pending].sets.length}
          suggested={suggested[exerciseKey(pendingEx.name)]}
          current={session.weights[pendingEx.id]}
          onSave={(value) => dispatch({ type: 'RESOLVE_WEIGHT', exerciseId: pendingEx.id, value })}
          onClose={() => dispatch({ type: 'RESOLVE_WEIGHT', exerciseId: pendingEx.id, value: null })}
        />
      )}
      {toast && (
        <div className="toast" role="status">
          {toast}
        </div>
      )}
    </>
  );
}
