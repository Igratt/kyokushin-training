import { useState, type CSSProperties } from 'react';
import type { Day, Program, Session } from '../types';
import { pickChoices, plural, setsText, versionsOf } from '../data/programs';
import { progress } from '../workout/engine';
import { Confirm, DayTag, ExerciseImage, TopBar } from '../ui';

interface Props {
  program: Program;
  day: Day;
  /** How many times this day was done before; variants alternate with it. */
  rotation: number;
  restOverrides: Record<string, number>;
  onSetRest: (key: string, seconds: number | null) => void;
  onStart: (choices: number[]) => void;
  onBack: () => void;
  active: Session | null;
}

export default function Preview(p: Props) {
  const [confirm, setConfirm] = useState(false);
  const [choices, setChoices] = useState<number[]>(() => pickChoices(p.day, p.rotation));
  const running = p.active && p.active.phase !== 'FINISHED' ? p.active : null;
  const runningProg = running ? progress(running) : null;
  const shown = p.day.exercises.map((ex, i) => versionsOf(ex)[choices[i] ?? 0] ?? versionsOf(ex)[0]);
  const totalSets = shown.reduce((n, e) => n + e.sets, 0);
  const variantsToday = choices.filter((c) => c > 0).length;
  const count = shown.length;
  const start = () => (running ? setConfirm(true) : p.onStart(choices));
  const swap = (i: number) =>
    setChoices((cs) => cs.map((c, j) => (j === i ? (c + 1) % versionsOf(p.day.exercises[i]).length : c)));

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
        {count} {plural(count, 'pratimas', 'pratimai', 'pratimų')} · {totalSets} {plural(totalSets, 'setas', 'setai', 'setų')}.
        {variantsToday > 0
          ? ` Šiandien ${variantsToday} ${plural(variantsToday, 'pratimas daromas', 'pratimai daromi', 'pratimų daroma')} kitu variantu, kad kūnas neprisitaikytų.`
          : ' Šiandien pagrindiniai variantai.'}{' '}
        Variantą ir poilsį gali pakeisti čia, prieš startą.
      </p>

      <ol className="ex-list">
        {p.day.exercises.map((base, i) => {
          const versions = versionsOf(base);
          const ex = shown[i];
          const key = `${p.program.id}/${ex.id}`;
          const override = p.restOverrides[key];
          const rest = override ?? ex.restSeconds;
          const changed = override !== undefined && override !== ex.restSeconds;
          const isVariant = (choices[i] ?? 0) > 0;
          return (
            <li key={base.id} className={'ex-row' + (isVariant ? ' is-variant' : '')}>
              <ExerciseImage src={ex.image} name={ex.name} className="thumb" />
              <div className="ex-main">
                <div className="ex-name">
                  <span className="num">{i + 1}</span>
                  {ex.name}
                </div>
                <div className="muted small">{setsText(ex)}</div>
                {versions.length > 1 && (
                  <button className="variant-btn" onClick={() => swap(i)} aria-label={`Keisti variantą: ${ex.name}`}>
                    <span className={'variant-chip' + (isVariant ? ' on' : '')}>{isVariant ? `variantas${ex.tag ? ': ' + ex.tag : ''}` : 'pagrindinis'}</span>
                    <span className="variant-swap">⇄ keisti</span>
                  </button>
                )}
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
            onYes={() => p.onStart(choices)}
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
