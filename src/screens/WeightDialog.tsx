import { useState, type CSSProperties } from 'react';
import type { Exercise } from '../types';
import { plural } from '../data/programs';
import { formatKg, formatWeight, parseWeight } from '../workout/engine';

interface Props {
  exercise: Exercise;
  color: string;
  setsDone: number;
  suggested?: number;
  current?: string;
  onSave: (value: string) => void;
  onClose: () => void;
}

/** Pops up after the last set of every exercise and blocks the screen until the weight is saved or the dialog is closed. */
export default function WeightDialog(p: Props) {
  const [value, setValue] = useState(() => p.current?.trim() || (p.suggested !== undefined ? formatKg(p.suggested) : ''));
  const kg = parseWeight(value);
  const step = (delta: number) => setValue((v) => formatKg(Math.max(0, Math.round(((parseWeight(v) ?? 0) + delta) * 100) / 100)));

  return (
    <div className="modal-backdrop">
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="wd-title" style={{ '--day': p.color } as CSSProperties}>
        <div className="eyebrow">
          {p.exercise.name} · {p.setsDone} {plural(p.setsDone, 'setas', 'setai', 'setų')}
        </div>
        <h2 id="wd-title" className="h-display modal-title">
          Kokį svorį naudojai?
        </h2>
        <div className="kg-row">
          <button type="button" className="btn-step" onClick={() => step(-2.5)} aria-label="Minus 2,5 kg">
            −2,5
          </button>
          <div className="kg-field">
            <input
              id="wd-kg"
              className="kg-input kg-big"
              inputMode="decimal"
              placeholder="0"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              aria-label="Svoris kilogramais"
            />
            <span className="unit">kg</span>
          </div>
          <button type="button" className="btn-step" onClick={() => step(2.5)} aria-label="Plius 2,5 kg">
            +2,5
          </button>
        </div>
        <div className="muted small">{p.suggested !== undefined ? `Praeitą kartą: ${formatWeight(p.suggested)}` : 'Su šiuo pratimu svorio dar nesi įrašęs.'}</div>
        <button type="button" className="btn btn-xl btn-day" disabled={kg === null} onClick={() => p.onSave(value)}>
          Išsaugoti
        </button>
        <button type="button" className="btn btn-ghost" onClick={p.onClose}>
          Uždaryti be svorio
        </button>
      </div>
    </div>
  );
}
