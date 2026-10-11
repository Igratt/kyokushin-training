import { useMemo, useState, type CSSProperties } from 'react';
import type { Session } from '../types';
import { exerciseKey } from '../data/programs';
import { formatDuration, formatWeight, toRecord, type Action } from '../workout/engine';
import { Confirm, DayTag, TopBar } from '../ui';

interface Props {
  session: Session;
  suggested: Record<string, number>;
  dispatch: (a: Action) => void;
  onClose: () => void;
  onDelete: () => void;
  onReopen: () => void;
}

export default function Complete({ session: s, suggested, dispatch, onClose, onDelete, onReopen }: Props) {
  const [confirm, setConfirm] = useState(false);
  const rec = useMemo(() => toRecord(s), [s]);

  return (
    <div className="screen" style={{ '--day': s.day.color } as CSSProperties}>
      <TopBar center={<DayTag label={s.day.name} color={s.day.color} />} />
      <h1 className="h-display title">Treniruotė baigta</h1>
      <div className="saved-note">✓ Išsaugota istorijoje</div>

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

      <p className="muted small">Svorį gali pataisyti: jis galioja visiems to pratimo setams.</p>
      <ul className="sum-list">
        {rec.exercises.map((e, i) => {
          const ex = s.day.exercises[i];
          const last = suggested[exerciseKey(ex.name)];
          return (
            <li key={e.exerciseId}>
              <div className="sum-name">
                {e.name}
                <span className="muted small">
                  {' '}
                  {e.sets.length}/{e.plannedSets} setai
                </span>
              </div>
              {e.sets.length > 0 && (
                <div className="row">
                  <input
                    className="kg-input kg-small"
                    inputMode="decimal"
                    placeholder="kg"
                    aria-label={'Svoris: ' + e.name}
                    value={s.weights[ex.id] ?? ''}
                    onChange={(ev) => dispatch({ type: 'SET_WEIGHT', exerciseId: ex.id, value: ev.target.value })}
                  />
                  <span className="muted small">kg{last !== undefined ? ` · praeitą kartą ${formatWeight(last)}` : ''}</span>
                </div>
              )}
              <div className="muted small">{e.sets.length ? e.sets.map((st) => `${formatWeight(st.weightKg)} × ${st.reps}`).join(' · ') : 'praleista'}</div>
              {e.note && <div className="small">„{e.note}“</div>}
            </li>
          );
        })}
      </ul>

      <textarea
        rows={3}
        placeholder="Bendra pastaba (nebūtina)"
        value={s.workoutNote ?? ''}
        onChange={(e) => dispatch({ type: 'SET_WORKOUT_NOTE', value: e.target.value })}
      />

      <div className="sticky-bottom">
        <button className="btn btn-xl btn-day" onClick={onClose}>
          Grįžti į pradžią
        </button>
        <div className="row nav-row">
          <button className="btn btn-ghost" onClick={onReopen}>
            ‹ Grįžti į treniruotę
          </button>
          <button className="btn btn-ghost danger-text" onClick={() => setConfirm(true)}>
            Ištrinti
          </button>
        </div>
        {confirm && <Confirm text="Ištrinti šią treniruotę iš istorijos?" yes="Ištrinti" no="Ne" danger onYes={onDelete} onNo={() => setConfirm(false)} />}
      </div>
    </div>
  );
}
