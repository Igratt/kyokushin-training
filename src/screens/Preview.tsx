import { useState, type CSSProperties } from 'react';
import type { Day, Program, Session } from '../types';
import { plural } from '../data/programs';
import { progress } from '../workout/engine';
import { Confirm, DayTag, ExerciseImage, TopBar } from '../ui';

interface Props {
  program: Program;
  day: Day;
  restOverrides: Record<string, number>;
  onSetRest: (key: string, seconds: number | null) => void;
  onStart: () => void;
  onBack: () => void;
  active: Session | null;
}

export default function Preview(p: Props) {
  const [confirm, setConfirm] = useState(false);
  const totalSets = p.day.exercises.reduce((n, e) => n + e.sets, 0);
  const running = p.active && p.active.phase !== 'FINISHED' ? p.active : null;
  const runningProg = running ? progress(running) : null;
  const start = () => (running ? setConfirm(true) : p.onStart());
  const count = p.day.exercises.length;

  return (
    <div className="screen" style={{ '--day': p.day.color } as CSSProperties}>
      <TopBar
        left={
          <button className="btn-icon" onClick={p.onBack} aria-label="Atgal">
            ‹
          </button>
        }
        center={<DayTag label={p.day.name} color={p.day.color} />}
      />
      <h1 className="h-display title">{p.day.subtitle ?? p.day.name}</h1>
      <p className="muted small">
        {count} {plural(count, 'pratimas', 'pratimai', 'pratimų')} · {totalSets} {plural(totalSets, 'setas', 'setai', 'setų')}. Poilsį po setu gali
        pakoreguoti čia, prieš startą.
      </p>

      <ol className="ex-list">
        {p.day.exercises.map((ex, i) => {
          const key = `${p.program.id}/${ex.id}`;
          const override = p.restOverrides[key];
          const rest = override ?? ex.restSeconds;
          const changed = override !== undefined && override !== ex.restSeconds;
          return (
            <li key={ex.id} className="ex-row">
              <ExerciseImage src={ex.image} name={ex.name} className="thumb" />
              <div className="ex-main">
                <div className="ex-name">
                  <span className="num">{i + 1}</span>
                  {ex.name}
                </div>
                <div className="muted small">
                  {ex.sets} × {ex.reps}
                </div>
              </div>
              <div className="rest-ctl">
                <button className="btn-mini" onClick={() => p.onSetRest(key, Math.max(15, rest - 15))} aria-label="Mažiau poilsio">
                  −
                </button>
                <span className={'rest-val' + (changed ? ' changed' : '')}>{rest} s</span>
                <button className="btn-mini" onClick={() => p.onSetRest(key, Math.min(600, rest + 15))} aria-label="Daugiau poilsio">
                  +
                </button>
                {changed && (
                  <button className="link-mini" onClick={() => p.onSetRest(key, null)}>
                    atstatyti
                  </button>
                )}
              </div>
            </li>
          );
        })}
      </ol>

      <div className="sticky-bottom">
        {confirm && running && runningProg ? (
          <Confirm
            text={`Pradėta ${running.day.name} (${runningProg.done}/${runningProg.planned} setų) bus užbaigta. Atlikti setai liks istorijoje.`}
            yes="Pradėti naują"
            no="Ne"
            onYes={p.onStart}
            onNo={() => setConfirm(false)}
          />
        ) : (
          <button className="btn btn-xl btn-day" onClick={start}>
            Pradėti treniruotę
          </button>
        )}
      </div>
    </div>
  );
}
