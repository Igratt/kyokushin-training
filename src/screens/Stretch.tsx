import { useEffect, useRef, type CSSProperties } from 'react';
import type { Session, Settings } from '../types';
import { stretchSteps } from '../data/programs';
import { formatClock, sideName, type Action } from '../workout/engine';
import { useAlarm, useNow, useWakeLock } from '../hooks';
import { nativeTimer } from '../native';
import { DayTag, ExerciseImage, ProgressBar, TopBar } from '../ui';

interface Props {
  session: Session;
  dispatch: (a: Action) => void;
  settings: Settings;
  onExit: () => void;
}

const RING = 2 * Math.PI * 54;
const sideLabel = (side: number) => (side ? sideName(side).replace(/^./, (c) => c.toUpperCase()) + ' pusė' : '');

/**
 * Guided warm-up (before the workout) or cool-down (after it):
 * get ready (5 s) → hold → next side / next item, with a short beep in between.
 */
export default function Stretch({ session: s, dispatch, settings, onExit }: Props) {
  const run = s.stretch;
  const now = useNow(!!run, 200);
  const alarm = useAlarm();
  useWakeLock(true);
  const firedFor = useRef<string>('');
  const warm = run?.list === 'warmup';
  const steps = stretchSteps(s.day, warm ? 'warmup' : 'cooldown');

  // Phase over: hold starts after "get ready" (soft tick), next step after a hold (short beep; the
  // Android app beeps natively, also with the screen off).
  useEffect(() => {
    if (!run || now < run.endsAt) return;
    const key = `${run.list ?? 'cooldown'}:${run.index}:${run.phase}:${run.endsAt}`;
    if (firedFor.current === key) return;
    firedFor.current = key;
    if (run.phase === 'prep') alarm.fire(settings, 'tick');
    else if (!nativeTimer) alarm.fire(settings, 'short');
    dispatch({ type: 'STRETCH_ADVANCE', now: Date.now() });
  }, [now, run, alarm, settings, dispatch]);

  if (!run) return null;
  const step = steps[run.index];
  if (!step) return null;
  const st = step.stretch;
  const next = steps[run.index + 1];
  const remainingMs = Math.max(0, run.endsAt - now);
  const frac = Math.min(1, Math.max(0, 1 - remainingMs / Math.max(1, run.total * 1000)));
  const prep = run.phase === 'prep';
  const color = s.day.color;
  const title = warm ? 'Apšilimas' : 'Tempimas';

  return (
    <div className="screen active stretch" style={{ '--day': color } as CSSProperties}>
      <TopBar
        left={
          <button className="btn-icon" onClick={onExit} aria-label={warm ? 'Baigti apšilimą' : 'Baigti tempimą'}>
            ✕
          </button>
        }
        center={
          <span className="top-center">
            <DayTag label={s.day.name} color={color} />
            <span className="top-ex">
              {title} {run.index + 1}/{steps.length}
            </span>
          </span>
        }
      />
      <ProgressBar percent={(run.index / steps.length) * 100} color={color} />
      <ExerciseImage src={st.image} name={st.name} className="ex-image stretch-image" />
      <div className="stretch-head">
        <h1 className="h-display ex-title">{st.name}</h1>
        {step.side > 0 && <span className="variant-chip on">{sideLabel(step.side)}</span>}
      </div>

      <div className="stretch-timer">
        <div className={'ring-wrap small' + (prep ? ' prep' : '')}>
          <svg viewBox="0 0 120 120" className="ring" aria-hidden="true">
            <circle cx="60" cy="60" r="54" className="ring-bg" />
            <circle cx="60" cy="60" r="54" className="ring-fg" style={{ strokeDasharray: RING, strokeDashoffset: RING * frac }} />
          </svg>
          <div className="ring-time h-display">{prep ? Math.ceil(remainingMs / 1000) : formatClock(Math.ceil(remainingMs / 1000))}</div>
        </div>
        <div className="stretch-info">
          <div className="rest-label">{prep ? (step.side === 2 ? 'Keisk pusę' : 'Pasiruošk') : warm ? 'Daryk' : 'Laikyk'}</div>
          {st.description && <p className="ex-desc">{st.description}</p>}
          {st.focus && <div className="muted small">Kam: {st.focus}</div>}
        </div>
      </div>
      <div className="muted small">
        {next
          ? `Toliau: ${next.stretch.name}${next.side ? ' · ' + sideLabel(next.side).toLowerCase() : ''}`
          : warm
            ? 'Paskutinis apšilimo pratimas, toliau treniruotė'
            : 'Paskutinis tempimas'}
      </div>

      <div className="sticky-bottom">
        <button className="btn btn-xl btn-day" id="stretch-next" onClick={() => dispatch({ type: 'STRETCH_SKIP', now: Date.now() })}>
          {next ? 'Kitas ›' : warm ? 'Į treniruotę ›' : 'Baigti tempimą'}
        </button>
        <div className="row nav-row">
          <button className="btn btn-ghost" disabled={run.index === 0} onClick={() => dispatch({ type: 'STRETCH_BACK', now: Date.now() })}>
            ‹ Atgal
          </button>
          <button className="btn btn-ghost" disabled={prep} onClick={() => dispatch({ type: 'STRETCH_ADD', seconds: 15, now: Date.now() })}>
            +15 s
          </button>
        </div>
      </div>
    </div>
  );
}
