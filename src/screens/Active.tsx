import { useEffect, useRef, useState, type CSSProperties } from 'react';
import type { Session, Settings } from '../types';
import { exerciseKey } from '../data/programs';
import { effectiveSets, formatClock, formatWeight, progress, restFor, type Action } from '../workout/engine';
import { useAlarm, useFullscreen, useNow, useWakeLock } from '../hooks';
import { isNative, nativeTimer } from '../native';
import { Confirm, DayTag, ExerciseImage, ProgressBar, TopBar } from '../ui';

interface Props {
  session: Session;
  dispatch: (a: Action) => void;
  settings: Settings;
  suggested: Record<string, number>;
  onExit: () => void;
}

const RING = 2 * Math.PI * 54;

export default function Active({ session: s, dispatch, settings, suggested, onExit }: Props) {
  const day = s.day;
  const resting = s.phase === 'RESTING';
  const now = useNow(resting, 200);
  const alarm = useAlarm();
  const fs = useFullscreen();
  useWakeLock(true);
  const [confirmExit, setConfirmExit] = useState(false);
  const [showNote, setShowNote] = useState(false);
  const [perSetOpen, setPerSetOpen] = useState(false);
  const [perSetText, setPerSetText] = useState('');
  const firedFor = useRef<number | null>(null);

  const ex = day.exercises[s.exerciseIndex];
  const done = s.logs[s.exerciseIndex].sets.length;
  const allDone = done >= ex.sets;
  const prog = progress(s);
  const color = day.color;
  const lastW = suggested[exerciseKey(ex.name)];
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

  const completeSet = () => {
    alarm.prime();
    dispatch({ type: 'COMPLETE_SET', now: Date.now(), perSetWeight: perSetOpen ? perSetText : undefined });
    setPerSetText('');
    setPerSetOpen(false);
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

  return (
    <div className="screen active" style={{ '--day': color } as CSSProperties}>
      {topBar}
      <div className="ex-head">
        {ex.focus && <div className="muted small">{ex.focus}</div>}
        <h1 className="h-display ex-title">{ex.name}</h1>
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
        <div className="muted small">Poilsis po seto: {restFor(s, s.exerciseIndex)} s</div>
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
          {exWeightText ? (
            <span className="muted small">Svoris: {exWeightText} kg</span>
          ) : lastW !== undefined ? (
            <span className="muted small">Praeitą kartą: {formatWeight(lastW)}</span>
          ) : null}
          {!allDone && (
            <button className="link small" onClick={() => setPerSetOpen(true)}>
              + svoris šiam setui
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
