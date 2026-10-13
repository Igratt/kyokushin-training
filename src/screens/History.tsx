import { useState, type CSSProperties } from 'react';
import type { WorkoutRecord } from '../types';
import { DEFAULT_PROGRAM_ID, dayColor } from '../data/programs';
import { formatDate, formatDuration, formatWeight } from '../workout/engine';
import { Confirm, DayTag, TopBar } from '../ui';

interface Props {
  history: WorkoutRecord[];
  activeId?: string;
  detailId?: string;
  onOpen: (id: string) => void;
  onBack: () => void;
  onDelete?: (id: string) => void;
}

const colorOf = (r: WorkoutRecord) => r.dayColor ?? dayColor(r.dayId, 0);
const nameOf = (r: WorkoutRecord) => r.dayName ?? `${r.dayId} DIENA`;

export default function History(p: Props) {
  const [confirm, setConfirm] = useState(false);
  const multiProgram = new Set(p.history.map((r) => r.programId ?? DEFAULT_PROGRAM_ID)).size > 1;
  const back = (
    <button className="btn-icon" onClick={p.onBack} aria-label="Atgal">
      ‹
    </button>
  );
  const status = (r: WorkoutRecord) =>
    r.completed === false ? (
      r.id === p.activeId ? (
        <span className="status-pill live">vyksta</span>
      ) : (
        <span className="status-pill partial">nebaigta</span>
      )
    ) : null;

  if (p.detailId) {
    const rec = p.history.find((r) => r.id === p.detailId);
    if (!rec) {
      return (
        <div className="screen">
          <TopBar left={back} />
          <p className="muted">Įrašas nerastas.</p>
        </div>
      );
    }
    return (
      <div className="screen" style={{ '--day': colorOf(rec) } as CSSProperties}>
        <TopBar left={back} center={<DayTag label={nameOf(rec)} color={colorOf(rec)} />} />
        <h1 className="h-display title">
          {formatDate(rec.finishedAt)} {status(rec)}
        </h1>
        {rec.programName && <p className="muted small">{rec.programName}</p>}
        {rec.stretched && <p className="small saved-note">✓ Tempimas atliktas</p>}
        <div className="stats">
          <div className="stat">
            <div className="h-display stat-num">{formatDuration(rec.durationSec)}</div>
            <div className="muted small">trukmė</div>
          </div>
          <div className="stat">
            <div className="h-display stat-num">
              {rec.totalSetsDone}/{rec.totalSetsPlanned}
            </div>
            <div className="muted small">setų atlikta</div>
          </div>
        </div>
        <ul className="sum-list">
          {rec.exercises.map((e) => (
            <li key={e.exerciseId}>
              <div className="sum-name">
                {e.name}
                <span className="muted small">
                  {' '}
                  {e.sets.length}/{e.plannedSets} setai
                </span>
              </div>
              <div className="muted small">{e.sets.length ? e.sets.map((st) => `${formatWeight(st.weightKg)} × ${st.reps}`).join(' · ') : 'praleista'}</div>
              {e.note && <div className="small">„{e.note}“</div>}
            </li>
          ))}
        </ul>
        {rec.note && <p className="card">„{rec.note}“</p>}
        {p.onDelete &&
          (confirm ? (
            <Confirm text="Ištrinti šią treniruotę iš istorijos?" yes="Ištrinti" no="Ne" danger onYes={() => p.onDelete!(rec.id)} onNo={() => setConfirm(false)} />
          ) : (
            <button className="btn btn-ghost danger-text" onClick={() => setConfirm(true)}>
              Ištrinti įrašą
            </button>
          ))}
      </div>
    );
  }

  return (
    <div className="screen">
      <TopBar left={back} center={<span className="top-ex">Istorija</span>} />
      {p.history.length === 0 ? (
        <p className="muted">Dar nėra treniruočių. Kiekvienas atliktas setas čia įsirašo automatiškai.</p>
      ) : (
        <ul className="hist-list">
          {p.history.map((r) => (
            <li key={r.id}>
              <button className="hist-row" style={{ '--day': colorOf(r) } as CSSProperties} onClick={() => p.onOpen(r.id)}>
                <span className="hist-day h-display">{r.dayId.slice(0, 2)}</span>
                <span className="hist-main">
                  <span>
                    {formatDate(r.finishedAt)} {status(r)}
                  </span>
                  <span className="muted small">
                    {formatDuration(r.durationSec)} · {r.totalSetsDone}/{r.totalSetsPlanned} setų
                    {multiProgram && r.programName ? ` · ${r.programName}` : ''}
                  </span>
                </span>
                <span className="chev">›</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
