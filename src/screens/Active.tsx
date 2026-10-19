import { useEffect, useRef, useState, type CSSProperties } from 'react';
import type { Session, Settings } from '../types';
import { exerciseKey, plural, stretchMinutes, stretchSteps } from '../data/programs';
import {
  effectiveSets,
  formatClock,
  formatKg,
  formatShortDate,
  formatWeight,
  progress,
  restFor,
  sideName,
  type Action,
  type LastPerformance,
} from '../workout/engine';
import { useAlarm, useFullscreen, useNow, useWakeLock } from '../hooks';
import { isNative, nativeTimer } from '../native';
import { Confirm, DayTag, ExerciseImage, ProgressBar, TopBar } from '../ui';

interface Props {
  session: Session;
  dispatch: (a: Action) => void;
  settings: Settings;
  suggested: Record<string, number>;
  /** Last time each exercise was done (by name). */
  last: Record<string, LastPerformance>;
  /** Start the guided warm-up of the day. */
  onWarmup: () => void;
  onExit: () => void;
}

const RING = 2 * Math.PI * 54;

/** "40 kg · 4 setai", "40 · 40 · 42,5 kg" or "svoris neįrašytas". */
function lastText(p: LastPerformance, timed: boolean, knownKg: number | undefined): string {
  const n = p.weights.length;
  const sets = `${n} ${plural(n, 'setas', 'setai', 'setų')}`;
  const kg = p.weights.filter((w): w is number => w !== null);
  if (kg.length === 0) {
    if (timed) return sets;
    return knownKg !== undefined ? `svoris neįrašytas · paskutinis įrašytas ${formatWeight(knownKg)}` : `${sets}, svoris neįrašytas`;
  }
  if (kg.length === n && kg.every((w) => w === kg[0])) return `${formatKg(kg[0])} kg · ${sets}`;
  return p.weights.map((w) => (w === null ? '—' : formatKg(w))).join(' · ') + ' kg';
}

export default function Active({ session: s, dispatch, settings, suggested, last, onWarmup, onExit }: Props) {
  const day = s.day;
  const resting = s.phase === 'RESTING';
  // Timer of a timed set (plank): "get ready" → hold (→ other side) → the set logs itself.
  const work = s.phase === 'ACTIVE_SET' ? s.work ?? null : null;
  const now = useNow(resting || !!work, 200);
  const alarm = useAlarm();
  const fs = useFullscreen();
  useWakeLock(true);
  const [confirmExit, setConfirmExit] = useState(false);
  const [showNote, setShowNote] = useState(false);
  const [perSetOpen, setPerSetOpen] = useState(false);
  const [perSetText, setPerSetText] = useState('');
  const firedFor = useRef<number | null>(null);
  const workFired = useRef('');

  const ex = day.exercises[s.exerciseIndex];
  const done = s.logs[s.exerciseIndex].sets.length;
  const allDone = done >= ex.sets;
  const timed = !!ex.seconds;
  const workLeftMs = work ? Math.max(0, work.endsAt - now) : 0;
  const workFrac = work ? Math.min(1, Math.max(0, 1 - workLeftMs / Math.max(1, work.total * 1000))) : 0;
  const prog = progress(s);
  const color = day.color;
  const lastW = suggested[exerciseKey(ex.name)];
  const lastPerf = last[exerciseKey(ex.name)];
  const exWeightText = s.weights[ex.id] ?? '';
  const doneSets = effectiveSets(s, s.exerciseIndex);

  useEffect(() => {
    setShowNote(false);
    setPerSetOpen(false);
    setPerSetText('');
  }, [ex.id]);

  // Rest finished: move on (and beep in the browser; the Android app rings natively, also in the background).
  // Works after a lock screen too, because `now` is re-read when the app becomes visible and the end time is absolute.
  useEffect(() => {
    if (!resting || s.restEndsAt === null) return;
    if (now >= s.restEndsAt && firedFor.current !== s.restEndsAt) {
      firedFor.current = s.restEndsAt;
      if (!nativeTimer) alarm.fire(settings);
      dispatch({ type: 'REST_DONE', now: Date.now() });
    }
  }, [now, resting, s.restEndsAt, alarm, settings, dispatch]);

  // Timed set: a soft tick when the hold starts, a short beep when it ends (the Android app beeps natively,
  // also with the screen off). The engine then switches side or logs the set and starts the rest.
  useEffect(() => {
    if (!work || now < work.endsAt) return;
    const key = `${work.phase}:${work.side}:${work.endsAt}`;
    if (workFired.current === key) return;
    workFired.current = key;
    if (work.phase === 'prep') alarm.fire(settings, 'tick');
    else if (!nativeTimer) alarm.fire(settings, 'short');
    dispatch({ type: 'WORK_ADVANCE', now: Date.now() });
  }, [now, work, alarm, settings, dispatch]);

  const completeSet = () => {
    alarm.prime();
    dispatch({ type: 'COMPLETE_SET', now: Date.now(), perSetWeight: perSetOpen ? perSetText : undefined });
    setPerSetText('');
    setPerSetOpen(false);
  };
  const startWork = () => {
    alarm.prime();
    dispatch({ type: 'WORK_START', now: Date.now() });
  };

  const topBar = (
    <>
      <TopBar
        left={
          <button className="btn-icon" onClick={() => setConfirmExit(true)} aria-label="Išeiti">
            ✕
          </button>
        }
        center={
          <span className="top-center">
            <DayTag label={day.name} color={color} />
            <span className="top-ex">
              Pratimas {s.exerciseIndex + 1}/{day.exercises.length}
            </span>
          </span>
        }
        right={
          fs.supported && !isNative ? (
            <button className="btn-icon" onClick={fs.toggle} aria-label="Visas ekranas">
              {fs.isFull ? '⤡' : '⛶'}
            </button>
          ) : null
        }
      />
      <ProgressBar percent={prog.percent} color={color} />
      {confirmExit && (
        <Confirm
          text="Išeiti į pradžią? Treniruotė lieka išsaugota, galėsi tęsti."
          yes="Į pradžią"
          no="Tęsti"
          onYes={onExit}
          onNo={() => setConfirmExit(false)}
          extra={
            <button className="btn btn-sm btn-danger" onClick={() => dispatch({ type: 'FINISH', now: Date.now() })}>
              Baigti treniruotę dabar
            </button>
          }
        />
      )}
    </>
  );

  if (resting && s.restTarget) {
    const remainingMs = Math.max(0, (s.restEndsAt ?? now) - now);
    const totalMs = Math.max(1, (s.restSeconds ?? 1) * 1000);
    const frac = Math.min(1, Math.max(0, 1 - remainingMs / totalMs));
    const target = s.restTarget;
    const nextEx = day.exercises[target.exerciseIndex];
    const afterExercise = s.restLabel === 'exercise';
    return (
      <div className="screen active" style={{ '--day': color } as CSSProperties}>
        {topBar}
        <div className="rest-view">
          <div className="rest-label">{afterExercise ? 'Poilsis prieš kitą pratimą' : `Poilsis prieš setą ${target.setIndex + 1}/${ex.sets}`}</div>
          <div className="ring-wrap">
            <svg viewBox="0 0 120 120" className="ring" aria-hidden="true">
              <circle cx="60" cy="60" r="54" className="ring-bg" />
              <circle cx="60" cy="60" r="54" className="ring-fg" style={{ strokeDasharray: RING, strokeDashoffset: RING * frac }} />
            </svg>
            <div className="ring-time h-display">{formatClock(Math.ceil(remainingMs / 1000))}</div>
          </div>
          <div className="next-card">
            <ExerciseImage src={nextEx.image} name={nextEx.name} className="next-img" />
            <div>
              <div className="muted small">{afterExercise ? 'Toliau' : 'Tas pats pratimas'}</div>
              <div className="next-name">{nextEx.name}</div>
              <div className="muted small">{afterExercise ? `${nextEx.sets} × ${nextEx.reps}` : `setas ${target.setIndex + 1}/${nextEx.sets}`}</div>
            </div>
          </div>
          <div className="row rest-btns">
            <button className="btn btn-ghost grow" onClick={() => dispatch({ type: 'ADJUST_REST', deltaSec: -15, now: Date.now() })}>
              −15 s
            </button>
            <button className="btn btn-ghost grow" onClick={() => dispatch({ type: 'ADJUST_REST', deltaSec: 30, now: Date.now() })}>
              +30 s
            </button>
          </div>
          <button className="btn btn-xl btn-day" onClick={() => dispatch({ type: 'SKIP_REST', now: Date.now() })}>
            Praleisti poilsį
          </button>
        </div>
      </div>
    );
  }

  // Timed set in progress: the same big ring as the rest, so the count is readable from the floor.
  if (work) {
    const prep = work.phase === 'prep';
    const leftSec = Math.min(work.total, Math.ceil(workLeftMs / 1000));
    return (
      <div className="screen active" style={{ '--day': color } as CSSProperties}>
        {topBar}
        <div className="rest-view" id="work-timer">
          <div className="rest-label">
            {prep ? (work.side === 2 ? 'Keisk pusę' : 'Pasiruošk') : 'Laikyk'}
            {work.side > 0 && (
              <span className="variant-chip on side-chip">{sideName(work.side, ex.startSide).replace(/^./, (c) => c.toUpperCase())} pusė</span>
            )}
          </div>
          <div className={'ring-wrap' + (prep ? ' prep' : '')}>
            <svg viewBox="0 0 120 120" className="ring" aria-hidden="true">
              <circle cx="60" cy="60" r="54" className="ring-bg" />
              <circle cx="60" cy="60" r="54" className="ring-fg" style={{ strokeDasharray: RING, strokeDashoffset: RING * workFrac }} />
            </svg>
            <div className="ring-time h-display">{prep ? leftSec : formatClock(leftSec)}</div>
          </div>
          <div className="next-card">
            <ExerciseImage src={ex.image} name={ex.name} className="next-img" />
            <div>
              <div className="muted small">Pratimas su laiku</div>
              <div className="next-name">{ex.name}</div>
              <div className="muted small">
                setas {done + 1}/{ex.sets} · {ex.seconds} s{ex.sides === 2 ? ' / pusė' : ''}
              </div>
            </div>
          </div>
          <div className="row rest-btns">
            <button className="btn btn-ghost grow" disabled={prep} onClick={() => dispatch({ type: 'WORK_ADD', seconds: 15, now: Date.now() })}>
              +15 s
            </button>
            <button className="btn btn-ghost grow" onClick={() => dispatch({ type: 'WORK_STOP' })}>
              Stabdyti
            </button>
          </div>
          <button className="btn btn-xl btn-day" id="set-done" onClick={completeSet}>
            ✓ Setas atliktas
          </button>
        </div>
      </div>
    );
  }

  // The day's warm-up is offered until the first set is done.
  const warmSteps = stretchSteps(day, 'warmup');
  const showWarm = warmSteps.length > 0 && prog.done === 0 && !s.warmedUp;
  const warmNames = (day.warmup ?? []).map((w) => w.name.replace(/\s*\(.*\)$/, ''));

  return (
    <div className="screen active" style={{ '--day': color } as CSSProperties}>
      {topBar}
      {showWarm && (
        <section className="card warm-card" id="warm-card">
          <div>
            <div className="stretch-card-title h-display">Apšilimas · ~{stretchMinutes(day, 'warmup')} min</div>
            <div className="muted small">
              {warmNames.slice(0, 3).join(', ')}
              {warmNames.length > 3 ? ` ir dar ${warmNames.length - 3}` : ''}
            </div>
          </div>
          <button className="btn btn-day" id="warm-start" onClick={onWarmup}>
            Pradėti apšilimą
          </button>
        </section>
      )}
      <div className="ex-head">
        {ex.focus && <div className="muted small">{ex.focus}</div>}
        <h1 className="h-display ex-title">{ex.name}</h1>
        {ex.choices && ex.choices.length > 1 && (
          <div className="row wrap variant-line">
            <span className={'variant-chip' + ((ex.choice ?? 0) > 0 ? ' on' : '')}>
              {(ex.choice ?? 0) > 0 ? `variantas${ex.tag ? ': ' + ex.tag : ''}` : 'pagrindinis'}
            </span>
            {done === 0 && (
              <button className="link small" onClick={() => dispatch({ type: 'SWAP_VARIANT', exerciseIndex: s.exerciseIndex })}>
                ⇄ Keisti į: {ex.choices[((ex.choice ?? 0) + 1) % ex.choices.length].name}
              </button>
            )}
          </div>
        )}
      </div>
      <ExerciseImage src={ex.image} name={ex.name} className="ex-image" />
      {ex.description && <p className="ex-desc">{ex.description}</p>}

      <div className="set-info">
        <div className="set-dots" aria-hidden="true">
          {Array.from({ length: ex.sets }, (_, i) => (
            <span key={i} className={'dot' + (i < done ? ' on' : !allDone && i === done ? ' cur' : '')} />
          ))}
        </div>
        <div className="set-line">
          <span className="h-display big">{allDone ? 'Visi setai atlikti' : `Setas ${done + 1} / ${ex.sets}`}</span>
          <span className="h-display big reps">{ex.reps}</span>
        </div>
        {ex.startSide && (
          <div className="side-line" id="side-line">
            Pradėk {ex.startSide === 'left' ? 'kaire' : 'dešine'} puse (silpnesnė), {ex.startSide === 'left' ? 'dešine' : 'kaire'} – tiek pat kartojimų
          </div>
        )}
        <div className="muted small">
          {timed ? `Laikmatis: ${ex.seconds} s${ex.sides === 2 ? ' / pusė' : ''} · ` : ''}Poilsis po seto: {restFor(s, s.exerciseIndex)} s
        </div>
        <div className="last-line" id="last-line">
          {lastPerf ? (
            <>
              Praeitą kartą ({formatShortDate(lastPerf.date)}): <b>{lastText(lastPerf, timed, lastW)}</b>
            </>
          ) : (
            <span className="muted">Praeitą kartą: dar nedarei</span>
          )}
        </div>
      </div>

      {perSetOpen ? (
        <div className="weight">
          <label className="muted small" htmlFor="kg-set">
            Svoris šiam setui, kg
          </label>
          <input id="kg-set" className="kg-input" inputMode="decimal" placeholder="kg" value={perSetText} onChange={(e) => setPerSetText(e.target.value)} />
        </div>
      ) : (
        <div className="row wrap weight-line">
          {exWeightText ? <span className="muted small">Šiandien: {exWeightText} kg</span> : null}
          {!allDone && (
            <button className="link small" onClick={() => setPerSetOpen(true)}>
              + svoris šiam setui
            </button>
          )}
          {timed && !work && !allDone && (
            <button className="link small" id="set-done-manual" onClick={completeSet}>
              ✓ atlikta be laikmačio
            </button>
          )}
        </div>
      )}

      {done > 0 && (
        <div className="done-list muted small">
          {doneSets.map((st) => (
            <span key={st.set}>
              ✓ {st.set}: {formatWeight(st.weightKg)}
              {st.perSet ? '*' : ''}
            </span>
          ))}
        </div>
      )}

      <button className="link" onClick={() => setShowNote((v) => !v)}>
        {showNote ? 'Slėpti pastabą' : 'Pastaba pratimui'}
      </button>
      {showNote && (
        <textarea
          rows={2}
          placeholder="pvz. kitą kartą +2,5 kg"
          value={s.notes[ex.id] ?? ''}
          onChange={(e) => dispatch({ type: 'SET_NOTE', exerciseId: ex.id, value: e.target.value })}
        />
      )}

      <div className="sticky-bottom">
        {allDone ? (
          s.exerciseIndex < day.exercises.length - 1 ? (
            <button className="btn btn-xl btn-day" onClick={() => dispatch({ type: 'NEXT_EXERCISE' })}>
              Kitas pratimas ›
            </button>
          ) : (
            <button className="btn btn-xl btn-day" onClick={() => dispatch({ type: 'FINISH', now: Date.now() })}>
              Baigti treniruotę
            </button>
          )
        ) : timed && !work ? (
          <button className="btn btn-xl btn-day" id="work-start" onClick={startWork}>
            ▶ Pradėti laikmatį · {ex.seconds} s{ex.sides === 2 ? ' / pusė' : ''}
          </button>
        ) : (
          <button className="btn btn-xl btn-day" id="set-done" onClick={completeSet}>
            ✓ Setas atliktas
          </button>
        )}
        <div className="row nav-row">
          <button className="btn btn-ghost" disabled={s.exerciseIndex === 0} onClick={() => dispatch({ type: 'PREV_EXERCISE' })}>
            ‹ Atgal
          </button>
          <button className="btn btn-ghost" disabled={prog.done === 0} onClick={() => dispatch({ type: 'UNDO_SET', now: Date.now() })}>
            Anuliuoti setą
          </button>
          <button className="btn btn-ghost" disabled={s.exerciseIndex >= day.exercises.length - 1} onClick={() => dispatch({ type: 'NEXT_EXERCISE' })}>
            Kitas ›
          </button>
        </div>
      </div>
    </div>
  );
}
