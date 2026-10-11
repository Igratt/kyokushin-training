import { useEffect, useState, type ReactNode } from 'react';

export function DayTag({ label, color }: { label: string; color: string }) {
  return (
    <span className="tag" style={{ background: color }}>
      {label}
    </span>
  );
}

export function ProgressBar({ percent, color }: { percent: number; color?: string }) {
  const p = Math.min(100, Math.max(0, percent));
  return (
    <div className="bar" role="progressbar" aria-valuenow={p} aria-valuemin={0} aria-valuemax={100}>
      <div className="bar-fill" style={{ width: `${p}%`, background: color }} />
    </div>
  );
}

export function TopBar({ left, center, right }: { left?: ReactNode; center?: ReactNode; right?: ReactNode }) {
  return (
    <div className="topbar">
      <div className="topbar-side">{left}</div>
      <div className="topbar-center">{center}</div>
      <div className="topbar-side right">{right}</div>
    </div>
  );
}

/** Exercise photo, or a neutral card with the name when the program has no picture (or it fails to load). */
export function ExerciseImage({ src, name, className }: { src?: string; name: string; className?: string }) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [src]);
  if (!src || failed) {
    return (
      <div className={'img-ph ' + (className ?? '')} role="img" aria-label={name}>
        <span>{name}</span>
      </div>
    );
  }
  return <img src={src} alt={name} className={className} onError={() => setFailed(true)} />;
}

export function Confirm({
  text,
  yes,
  no,
  onYes,
  onNo,
  danger,
  extra,
}: {
  text: string;
  yes: string;
  no: string;
  onYes: () => void;
  onNo: () => void;
  danger?: boolean;
  extra?: ReactNode;
}) {
  return (
    <div className="confirm" role="alertdialog">
      <span>{text}</span>
      <div className="row wrap">
        <button className={'btn btn-sm ' + (danger ? 'btn-danger' : 'btn-day')} onClick={onYes}>
          {yes}
        </button>
        <button className="btn btn-sm btn-ghost" onClick={onNo}>
          {no}
        </button>
        {extra}
      </div>
    </div>
  );
}
