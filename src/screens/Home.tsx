import { useState, type CSSProperties } from 'react';
import type { Program, Session, WorkoutRecord } from '../types';
import { plural } from '../data/programs';
import { formatDate, lastDoneByDay, progress } from '../workout/engine';
import { Confirm, DayTag } from '../ui';

interface Props {
  program: Program;
  session: Session | null;
  history: WorkoutRecord[];
  onPickDay: (dayId: string) => void;
  onResume: () => void;
  onFinishActive: () => void;
  onCloseFinished: () => void;
  onHistory: () => void;
  onSettings: () => void;
}

export default function Home(p: Props) {
  const [confirmFinish, setConfirmFinish] = useState(false);
  const lastByDay = lastDoneByDay(p.history, p.program.id);
  const newest = p.history[0];
  const s = p.session;
  const prog = s ? progress(s) : null;

  return (
    <div className="screen home">
      <header className="hero" style={{ backgroundImage: 'url(assets/cover.webp)' }}>
        <div className="hero-shade" />
        <div className="hero-text">
          <div className="eyebrow">{p.program.focus ?? `${p.program.days.length} ${plural(p.program.days.length, 'dienos', 'dienų', 'dienų')} programa`}</div>
          <h1 className="h-display hero-title">
            Kyokushin
            <br />
            Training
          </h1>
          <p className="muted small">{p.program.programName}</p>
        </div>
      </header>

      {s && prog && (
        <section className="card resume" style={{ '--day': s.day.color } as CSSProperties}>
          <div className="row between">
            <DayTag label={s.day.name} color={s.day.color} />
            <span className="muted small">pradėta {formatDate(s.startedAt)}</span>
          </div>
          {s.phase === 'FINISHED' ? (
            <>
              <div className="resume-title">Treniruotė baigta ir išsaugota</div>
              <div className="row">
                <button className="btn btn-day grow" onClick={p.onResume}>
                  Peržiūrėti
                </button>
                <button className="btn btn-ghost" onClick={p.onCloseFinished}>
                  Uždaryti
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="resume-title">
                Pratimas {s.exerciseIndex + 1}/{s.day.exercises.length} · atlikta {prog.done}/{prog.planned} setų
              </div>
              <div className="row">
                <button className="btn btn-day grow" onClick={p.onResume}>
                  Tęsti treniruotę
                </button>
                <button className="btn btn-ghost" onClick={() => setConfirmFinish(true)}>
                  Užbaigti
                </button>
              </div>
              {confirmFinish && (
                <Confirm
                  text="Užbaigti treniruotę dabar? Atlikti setai jau išsaugoti istorijoje."
                  yes="Užbaigti"
                  no="Ne"
                  onYes={() => {
                    setConfirmFinish(false);
                    p.onFinishActive();
                  }}
                  onNo={() => setConfirmFinish(false)}
                />
              )}
            </>
          )}
        </section>
      )}

      <section className="days">
        {p.program.days.map((d) => (
          <button key={d.id} className="day-card" style={{ '--day': d.color } as CSSProperties} onClick={() => p.onPickDay(d.id)}>
            <span className="day-letter h-display">{d.id.length <= 2 ? d.id : d.id.slice(0, 1)}</span>
            <span className="day-body">
              <span className="day-name h-display">{d.name}</span>
              {d.subtitle && <span className="day-sub">{d.subtitle}</span>}
              <span className="muted small">{lastByDay[d.id] ? 'Paskutinį kartą: ' + formatDate(lastByDay[d.id]) : 'Dar nedaryta'}</span>
            </span>
            <span className="chev">›</span>
          </button>
        ))}
      </section>

      <section className="row between wrap">
        <div className="muted small">{newest ? 'Paskutinė treniruotė: ' + formatDate(newest.finishedAt) : 'Treniruočių dar nėra'}</div>
        <div className="row">
          <button className="btn btn-outline" onClick={p.onHistory}>
            Istorija ({p.history.length})
          </button>
          <button className="btn btn-outline" onClick={p.onSettings}>
            Nustatymai
          </button>
        </div>
      </section>
    </div>
  );
}
