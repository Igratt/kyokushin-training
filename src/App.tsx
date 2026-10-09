import { useCallback, useEffect, useMemo, useState, type ReactElement } from 'react';
import { App as CapacitorApp } from '@capacitor/app';
import type { DayId, Session, Settings, WorkoutRecord } from './types';
import { getDay } from './data/program';
import { isNative } from './native';
import { storage } from './storage';
import { createSession, lastWeights, reduce, toRecord, type Action } from './workout/engine';
import Home from './screens/Home';
import Preview from './screens/Preview';
import Active from './screens/Active';
import Complete from './screens/Complete';
import History from './screens/History';

type View =
  | { name: 'home' }
  | { name: 'preview'; dayId: DayId }
  | { name: 'active' }
  | { name: 'complete' }
  | { name: 'history' }
  | { name: 'historyDetail'; id: string };

export default function App() {
  const [view, setView] = useState<View>({ name: 'home' });
  const [session, setSession] = useState<Session | null>(() => storage.loadSession());
  const [history, setHistory] = useState<WorkoutRecord[]>(() => storage.loadHistory());
  const [restOverrides, setRestOverrides] = useState<Record<string, number>>(() => storage.loadRestOverrides());
  const [settings, setSettings] = useState<Settings>(() => storage.loadSettings());
  const [toast, setToast] = useState<string | null>(null);

  // Everything that matters survives a refresh or a closed tab.
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
    if (!toast) return;
    const id = window.setTimeout(() => setToast(null), 2500);
    return () => window.clearTimeout(id);
  }, [toast]);

  // Android hardware back button: step back through the screens instead of closing the app.
  // A workout in progress stays saved, so leaving it is always safe.
  useEffect(() => {
    if (!isNative) return;
    const handle = CapacitorApp.addListener('backButton', () => {
      setView((v) => {
        if (v.name === 'home') {
          CapacitorApp.minimizeApp().catch(() => undefined);
          return v;
        }
        if (v.name === 'historyDetail') return { name: 'history' };
        if (v.name === 'complete') return v;
        return { name: 'home' };
      });
    });
    return () => {
      handle.then((h) => h.remove()).catch(() => undefined);
    };
  }, []);

  const dispatch = useCallback((a: Action) => {
    setSession((s) => (s ? reduce(s, getDay(s.dayId), a) : s));
  }, []);
  const suggested = useMemo(() => lastWeights(history), [history]);

  const startWorkout = (dayId: DayId) => {
    setSession(createSession(getDay(dayId), { restOverrides, suggestedWeights: suggested, now: Date.now() }));
    setView({ name: 'active' });
  };
  const resume = () => {
    if (!session) return;
    setView(session.phase === 'FINISHED' ? { name: 'complete' } : { name: 'active' });
  };
  const discard = () => {
    setSession(null);
    setView({ name: 'home' });
  };
  const save = (note: string) => {
    if (!session) return;
    const rec = toRecord(session, getDay(session.dayId), note);
    setHistory((h) => [rec, ...h.filter((r) => r.id !== rec.id)]);
    setSession(null);
    setView({ name: 'home' });
    setToast('Treniruotė išsaugota');
  };
  const deleteRecord = (id: string) => {
    setHistory((h) => h.filter((r) => r.id !== id));
    setView({ name: 'history' });
    setToast('Įrašas ištrintas');
  };
  const setRest = (exerciseId: string, seconds: number | null) =>
    setRestOverrides((o) => {
      const next = { ...o };
      if (seconds === null) delete next[exerciseId];
      else next[exerciseId] = seconds;
      return next;
    });

  // The last set of the last exercise finishes the workout: jump to the summary.
  useEffect(() => {
    if (session?.phase === 'FINISHED' && view.name === 'active') setView({ name: 'complete' });
  }, [session?.phase, view.name]);
  useEffect(() => {
    if (!session && (view.name === 'active' || view.name === 'complete')) setView({ name: 'home' });
  }, [session, view.name]);

  let screen: ReactElement;
  switch (view.name) {
    case 'preview':
      screen = (
        <Preview
          day={getDay(view.dayId)}
          restOverrides={restOverrides}
          onSetRest={setRest}
          onStart={() => startWorkout(view.dayId)}
          onBack={() => setView({ name: 'home' })}
          hasActive={!!session}
        />
      );
      break;
    case 'active':
      screen = session ? (
        <Active session={session} day={getDay(session.dayId)} dispatch={dispatch} settings={settings} suggested={suggested} onExit={() => setView({ name: 'home' })} />
      ) : (
        <></>
      );
      break;
    case 'complete':
      screen = session ? (
        <Complete
          session={session}
          day={getDay(session.dayId)}
          suggested={suggested}
          dispatch={dispatch}
          onSave={save}
          onDiscard={discard}
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
      screen = <History history={history} onOpen={(id) => setView({ name: 'historyDetail', id })} onBack={() => setView({ name: 'home' })} />;
      break;
    case 'historyDetail':
      screen = (
        <History
          history={history}
          detailId={view.id}
          onOpen={(id) => setView({ name: 'historyDetail', id })}
          onBack={() => setView({ name: 'history' })}
          onDelete={deleteRecord}
        />
      );
      break;
    default:
      screen = (
        <Home
          session={session}
          history={history}
          settings={settings}
          onSettings={setSettings}
          onPickDay={(d) => setView({ name: 'preview', dayId: d })}
          onResume={resume}
          onDiscard={discard}
          onHistory={() => setView({ name: 'history' })}
        />
      );
  }

  return (
    <>
      {screen}
      {toast && (
        <div className="toast" role="status">
          {toast}
        </div>
      )}
    </>
  );
}
