import { useMemo, useState, type CSSProperties } from 'react';
import type { Day, Session } from '../types';
import { DAY_COLORS, OPTIONAL_WEIGHT } from '../data/program';
import { formatDuration, formatWeight, toRecord, type Action } from '../workout/engine';
import { Confirm, DayTag, TopBar } from '../ui';

interface Props {
  session: Session;
  day: Day;
  suggested: Record<string, number>;
  dispatch: (a: Action) => void;
  onSave: (note: string) => void;
  onDiscard: () => void;
  onReopen: () => void;
}

export default function Complete({ session: s, day, suggested, dispatch, onSave, onDiscard, onReopen }: Props) {
  const [note, setNote] = useState('');
  const [confirm, setConfirm] = useState(false);
  const rec = useMemo(() => toRecord(s, day, note), [s, day, note]);

  return (
    <div className="screen" style={{ '--day': DAY_COLORS[day.id] } as CSSProperties}>
      <TopBar center={<DayTag dayId={day.id} />} />
      <h1 className="h-display title">Treniruotė baigta</h1>

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

      <p className="muted small">Patikrink svorius: lauką gali pataisyti, jis galioja visiems to pratimo setams.</p>
      <ul className="sum-list">
        {rec.exercises.map((e, i) => {
          const ex = day.exercises[i];
          const last = suggested[ex.id];
          return (
            <li key={e.exerciseId}>
              <div className="sum-name">
                {e.name}
                <span className="muted small">
                  {' '}
                  {e.sets.length}/{e.plannedSets} setai
                </span>
              </div>
              {e.sets.length > 0 && !OPTIONAL_WEIGHT.has(ex.id) && (
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

      <textarea rows={3} placeholder="Bendra pastaba (nebūtina)" value={note} onChange={(e) => setNote(e.target.value)} />

      <div className="sticky-bottom">
        <button className="btn btn-xl btn-day" onClick={() => onSave(note)}>
          Išsaugoti treniruotę
        </button>
        <div className="row nav-row">
          <button className="btn btn-ghost" onClick={onReopen}>
            ‹ Grįžti į treniruotę
          </button>
          <button className="btn btn-ghost" onClick={() => setConfirm(true)}>
            Į pradžią neišsaugojus
          </button>
        </div>
        {confirm && <Confirm text="Neišsaugota treniruotė bus prarasta." yes="Prarasti" no="Ne" danger onYes={onDiscard} onNo={() => setConfirm(false)} />}
      </div>
    </div>
  );
}
