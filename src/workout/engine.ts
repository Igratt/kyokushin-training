import type { Day, DayId, Position, Session, SetLog, WorkoutRecord } from '../types';

/*
 * Workout state machine. Pure functions only, so the whole flow can be reasoned about
 * (and tested) without React:
 *
 *   ACTIVE_SET --COMPLETE_SET--> RESTING --(timer / skip)--> ACTIVE_SET ... --> FINISHED
 *
 * Rest is stored as an absolute end timestamp, so a locked phone or a closed tab
 * never pauses it.
 */

export type Action =
  | { type: 'COMPLETE_SET'; now: number; perSetWeight?: string }
  | { type: 'REST_DONE'; now: number }
  | { type: 'SKIP_REST'; now: number }
  | { type: 'ADJUST_REST'; deltaSec: number; now: number }
  | { type: 'PREV_EXERCISE' }
  | { type: 'NEXT_EXERCISE' }
  | { type: 'UNDO_SET'; now: number }
  | { type: 'SET_WEIGHT'; exerciseId: string; value: string }
  | { type: 'SET_NOTE'; exerciseId: string; value: string }
  | { type: 'FINISH'; now: number }
  | { type: 'REOPEN' };

const DOUBLE_TAP_MS = 700;

export function createSession(
  day: Day,
  opts: { restOverrides: Record<string, number>; suggestedWeights: Record<string, number>; now: number },
): Session {
  const weights: Record<string, string> = {};
  for (const ex of day.exercises) {
    const w = opts.suggestedWeights[ex.id];
    if (w !== undefined) weights[ex.id] = String(w);
  }
  return {
    dayId: day.id,
    startedAt: new Date(opts.now).toISOString(),
    phase: 'ACTIVE_SET',
    exerciseIndex: 0,
    setIndex: 0,
    restEndsAt: null,
    restSeconds: null,
    restTarget: null,
    restLabel: null,
    logs: day.exercises.map((ex) => ({ exerciseId: ex.id, sets: [] })),
    weights,
    notes: {},
    restOverrides: { ...opts.restOverrides },
    lastActionAt: 0,
  };
}

export function restFor(session: Session, day: Day, exerciseIndex: number): number {
  const ex = day.exercises[exerciseIndex];
  const override = session.restOverrides[ex.id];
  return override !== undefined && override > 0 ? override : ex.restSeconds;
}

export function parseWeight(text: string | undefined): number | null {
  if (!text) return null;
  const n = parseFloat(text.replace(',', '.'));
  return Number.isFinite(n) && n > 0 ? n : null;
}

function nextIncompleteAfter(session: Session, day: Day, from: number): number | null {
  for (let i = from + 1; i < day.exercises.length; i++) {
    if (session.logs[i].sets.length < day.exercises[i].sets) return i;
  }
  return null;
}

function positionFor(session: Session, day: Day, exerciseIndex: number): Position {
  const done = session.logs[exerciseIndex].sets.length;
  return { exerciseIndex, setIndex: Math.min(done, day.exercises[exerciseIndex].sets - 1) };
}

export function reduce(s: Session, day: Day, a: Action): Session {
  switch (a.type) {
    case 'COMPLETE_SET': {
      if (s.phase !== 'ACTIVE_SET') return s;
      if (a.now - s.lastActionAt < DOUBLE_TAP_MS) return s;
      const ex = day.exercises[s.exerciseIndex];
      const log = s.logs[s.exerciseIndex];
      if (log.sets.length >= ex.sets) return s;
      // Weight is normally asked once per exercise (see effectiveSets); a value typed for this set wins.
      const perSetKg = parseWeight(a.perSetWeight);
      const newLog = {
        ...log,
        sets: [
          ...log.sets,
          { set: log.sets.length + 1, reps: ex.reps, weightKg: perSetKg, perSet: perSetKg !== null, completedAt: new Date(a.now).toISOString() },
        ],
      };
      const logs = s.logs.map((l, i) => (i === s.exerciseIndex ? newLog : l));
      const withLogs = { ...s, logs, lastActionAt: a.now };
      let target: Position | null = null;
      let label: 'set' | 'exercise' | null = null;
      if (newLog.sets.length < ex.sets) {
        target = { exerciseIndex: s.exerciseIndex, setIndex: newLog.sets.length };
        label = 'set';
      } else {
        const next = nextIncompleteAfter(withLogs, day, s.exerciseIndex);
        if (next !== null) {
          target = { exerciseIndex: next, setIndex: logs[next].sets.length };
          label = 'exercise';
        }
      }
      if (!target) {
        return { ...withLogs, phase: 'FINISHED', finishedAt: new Date(a.now).toISOString(), restEndsAt: null, restSeconds: null, restTarget: null, restLabel: null };
      }
      const rest = restFor(s, day, s.exerciseIndex);
      return { ...withLogs, phase: 'RESTING', restEndsAt: a.now + rest * 1000, restSeconds: rest, restTarget: target, restLabel: label };
    }
    case 'REST_DONE':
    case 'SKIP_REST': {
      if (s.phase !== 'RESTING' || !s.restTarget) return s;
      return {
        ...s,
        phase: 'ACTIVE_SET',
        exerciseIndex: s.restTarget.exerciseIndex,
        setIndex: s.restTarget.setIndex,
        restEndsAt: null,
        restSeconds: null,
        restTarget: null,
        restLabel: null,
        lastActionAt: a.now,
      };
    }
    case 'ADJUST_REST': {
      if (s.phase !== 'RESTING' || s.restEndsAt === null) return s;
      const endsAt = Math.max(a.now + 1000, s.restEndsAt + a.deltaSec * 1000);
      const total = Math.max(1, (s.restSeconds ?? 0) + a.deltaSec);
      return { ...s, restEndsAt: endsAt, restSeconds: total };
    }
    case 'PREV_EXERCISE': {
      if (s.phase !== 'ACTIVE_SET' || s.exerciseIndex === 0) return s;
      return { ...s, ...positionFor(s, day, s.exerciseIndex - 1) };
    }
    case 'NEXT_EXERCISE': {
      if (s.phase !== 'ACTIVE_SET' || s.exerciseIndex >= day.exercises.length - 1) return s;
      return { ...s, ...positionFor(s, day, s.exerciseIndex + 1) };
    }
    case 'UNDO_SET': {
      let bestIdx = -1;
      let bestTime = '';
      s.logs.forEach((l, i) => {
        const last = l.sets[l.sets.length - 1];
        if (last && last.completedAt > bestTime) {
          bestTime = last.completedAt;
          bestIdx = i;
        }
      });
      if (bestIdx < 0) return s;
      const logs = s.logs.map((l, i) => (i === bestIdx ? { ...l, sets: l.sets.slice(0, -1) } : l));
      return {
        ...s,
        logs,
        phase: 'ACTIVE_SET',
        exerciseIndex: bestIdx,
        setIndex: logs[bestIdx].sets.length,
        restEndsAt: null,
        restSeconds: null,
        restTarget: null,
        restLabel: null,
        finishedAt: undefined,
        lastActionAt: a.now,
      };
    }
    case 'SET_WEIGHT':
      return { ...s, weights: { ...s.weights, [a.exerciseId]: a.value } };
    case 'SET_NOTE':
      return { ...s, notes: { ...s.notes, [a.exerciseId]: a.value } };
    case 'FINISH': {
      if (s.phase === 'FINISHED') return s;
      return { ...s, phase: 'FINISHED', finishedAt: new Date(a.now).toISOString(), restEndsAt: null, restSeconds: null, restTarget: null, restLabel: null };
    }
    case 'REOPEN': {
      if (s.phase !== 'FINISHED') return s;
      return { ...s, phase: 'ACTIVE_SET', finishedAt: undefined, ...positionFor(s, day, s.exerciseIndex) };
    }
    default:
      return s;
  }
}

export function progress(session: Session, day: Day): { done: number; planned: number; percent: number } {
  const planned = day.exercises.reduce((n, e) => n + e.sets, 0);
  const done = session.logs.reduce((n, l) => n + l.sets.length, 0);
  return { done, planned, percent: planned ? Math.round((done / planned) * 100) : 0 };
}

/** Sets of one exercise with the weight resolved: a weight typed for that set wins, otherwise the exercise-level weight. */
export function effectiveSets(session: Session, day: Day, exerciseIndex: number): SetLog[] {
  const ex = day.exercises[exerciseIndex];
  const exerciseKg = parseWeight(session.weights[ex.id]);
  return session.logs[exerciseIndex].sets.map((st) => (st.perSet ? st : { ...st, weightKg: exerciseKg }));
}

export function toRecord(session: Session, day: Day, note: string): WorkoutRecord {
  const finishedAt = session.finishedAt ?? new Date().toISOString();
  const { done, planned } = progress(session, day);
  return {
    id: finishedAt + '-' + day.id,
    dayId: day.id,
    startedAt: session.startedAt,
    finishedAt,
    durationSec: Math.max(0, Math.round((Date.parse(finishedAt) - Date.parse(session.startedAt)) / 1000)),
    totalSetsDone: done,
    totalSetsPlanned: planned,
    exercises: day.exercises.map((ex, i) => ({
      exerciseId: ex.id,
      name: ex.name,
      plannedSets: ex.sets,
      reps: ex.reps,
      sets: effectiveSets(session, day, i),
      note: session.notes[ex.id]?.trim() || undefined,
    })),
    note: note.trim() || undefined,
  };
}

/** Last weight used per exercise id across history, newest first. */
export function lastWeights(history: WorkoutRecord[]): Record<string, number> {
  const out: Record<string, number> = {};
  const sorted = [...history].sort((a, b) => b.finishedAt.localeCompare(a.finishedAt));
  for (const rec of sorted) {
    for (const ex of rec.exercises) {
      if (out[ex.exerciseId] !== undefined) continue;
      const withWeight = [...ex.sets].reverse().find((s) => s.weightKg !== null);
      if (withWeight && withWeight.weightKg !== null) out[ex.exerciseId] = withWeight.weightKg;
    }
  }
  return out;
}

export function lastDoneByDay(history: WorkoutRecord[]): Partial<Record<DayId, string>> {
  const out: Partial<Record<DayId, string>> = {};
  for (const rec of history) {
    if (!out[rec.dayId] || rec.finishedAt > (out[rec.dayId] as string)) out[rec.dayId] = rec.finishedAt;
  }
  return out;
}

export function formatClock(totalSec: number): string {
  const s = Math.max(0, Math.round(totalSec));
  const m = Math.floor(s / 60);
  return String(m).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
}

export function formatDuration(totalSec: number): string {
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  return h > 0 ? `${h} val. ${m} min.` : `${m} min.`;
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleDateString('lt-LT', { year: 'numeric', month: '2-digit', day: '2-digit' }) + ' ' + d.toLocaleTimeString('lt-LT', { hour: '2-digit', minute: '2-digit' });
}

export function formatWeight(kg: number | null): string {
  if (kg === null) return '—';
  return (Number.isInteger(kg) ? String(kg) : kg.toFixed(1).replace('.', ',')) + ' kg';
}
