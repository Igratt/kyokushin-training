import type { Day, Exercise, GuidedList, Position, Program, Session, SetLog, WorkRun, WorkoutRecord } from '../types';
import { DEFAULT_PROGRAM_ID, STRETCH_PREP_SECONDS, exerciseKey, stretchSteps, versionsOf, withChoice } from '../data/programs';

/*
 * Workout state machine. Pure functions only:
 *
 *   ACTIVE_SET --COMPLETE_SET--> RESTING --(timer / skip)--> ACTIVE_SET ... --> FINISHED
 *
 * Rest is stored as an absolute end timestamp, so a locked phone or a closed app never pauses it.
 * After the last set of an exercise, `pendingWeightFor` opens the "what weight did you use?" dialog.
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
  | { type: 'RESOLVE_WEIGHT'; exerciseId: string; value: string | null }
  | { type: 'SET_NOTE'; exerciseId: string; value: string }
  | { type: 'SET_WORKOUT_NOTE'; value: string }
  | { type: 'SWAP_VARIANT'; exerciseIndex: number }
  | { type: 'STRETCH_START'; now: number; list?: GuidedList }
  | { type: 'STRETCH_ADVANCE'; now: number }
  | { type: 'STRETCH_SKIP'; now: number }
  | { type: 'STRETCH_BACK'; now: number }
  | { type: 'STRETCH_ADD'; seconds: number; now: number }
  | { type: 'STRETCH_EXIT' }
  | { type: 'WORK_START'; now: number }
  | { type: 'WORK_ADVANCE'; now: number }
  | { type: 'WORK_ADD'; seconds: number; now: number }
  | { type: 'WORK_STOP' }
  | { type: 'FINISH'; now: number }
  | { type: 'REOPEN' };

const DOUBLE_TAP_MS = 700;
/** Finishing a workout long after its last set (e.g. the next day) dates it to that last set. */
const STALE_FINISH_MS = 30 * 60 * 1000;
/** Seconds of "get ready" before a timed set (plank) and between its two sides. */
export const WORK_PREP_SECONDS = 5;
/** A timed-set phase that ended this long ago was not followed (phone put away): drop the timer instead of logging the set. */
const STALE_WORK_MS = 60 * 1000;

const NO_REST = { restEndsAt: null, restSeconds: null, restTarget: null, restLabel: null } as const;

function newId(now: number): string {
  return now.toString(36) + '-' + Math.random().toString(36).slice(2, 8);
}

function clone<T>(v: T): T {
  return JSON.parse(JSON.stringify(v)) as T;
}

export function createSession(
  program: Program,
  day: Day,
  opts: { restOverrides: Record<string, number>; now: number; choices?: number[] },
): Session {
  // The snapshot holds the version chosen for each exercise (base or a variant) plus the alternatives.
  const snapshot: Day = { ...clone(day), exercises: day.exercises.map((ex, i) => withChoice(clone(ex), opts.choices?.[i] ?? 0)) };
  const rest: Record<string, number> = {};
  for (const ex of snapshot.exercises) {
    for (const v of versionsOf(ex)) {
      const o = opts.restOverrides[`${program.id}/${v.id}`];
      if (o !== undefined) rest[v.id] = o;
    }
  }
  return {
    id: newId(opts.now),
    programId: program.id,
    programName: program.programName,
    dayId: day.id,
    day: snapshot,
    startedAt: new Date(opts.now).toISOString(),
    phase: 'ACTIVE_SET',
    exerciseIndex: 0,
    setIndex: 0,
    ...NO_REST,
    logs: snapshot.exercises.map((ex) => ({ exerciseId: ex.id, sets: [] })),
    weights: {},
    notes: {},
    restOverrides: rest,
    lastActionAt: 0,
    pendingWeightFor: null,
  };
}

/** Brings a stored session up to the current shape (older app versions saved fewer fields). */
export function migrateSession(raw: unknown, programs: Program[]): Session | null {
  if (!raw || typeof raw !== 'object') return null;
  const s = raw as Partial<Session>;
  if (!s.dayId || !Array.isArray(s.logs)) return null;
  const programId = s.programId ?? DEFAULT_PROGRAM_ID;
  const program = programs.find((p) => p.id === programId) ?? programs.find((p) => p.id === DEFAULT_PROGRAM_ID);
  let day = s.day && Array.isArray(s.day.exercises) && s.day.exercises.length ? s.day : undefined;
  if (!day) {
    const fromProgram = program?.days.find((d) => d.id === s.dayId);
    if (!fromProgram) return null;
    day = clone(fromProgram);
  }
  if (!day.color) day = { ...day, color: program?.days.find((d) => d.id === day?.id)?.color ?? '#3B82F6' };
  // Workouts started before the cool-down / warm-up existed still get the day's lists.
  if (!day.stretches?.length) {
    const fromProgram = program?.days.find((d) => d.id === day?.id)?.stretches;
    if (fromProgram?.length) day = { ...day, stretches: clone(fromProgram) };
  }
  if (!day.warmup?.length) {
    const fromProgram = program?.days.find((d) => d.id === day?.id)?.warmup;
    if (fromProgram?.length) day = { ...day, warmup: clone(fromProgram) };
  }
  const oldLogs = s.logs;
  const logs = day.exercises.map((ex, i) => {
    const found = oldLogs[i]?.exerciseId === ex.id ? oldLogs[i] : oldLogs.find((l) => l?.exerciseId === ex.id);
    return found && Array.isArray(found.sets) ? found : { exerciseId: ex.id, sets: [] };
  });
  const count = day.exercises.length;
  const exerciseIndex = Math.min(Math.max(0, s.exerciseIndex ?? 0), count - 1);
  const targetOk = !!s.restTarget && s.restTarget.exerciseIndex >= 0 && s.restTarget.exerciseIndex < count;
  const resting = s.phase === 'RESTING' && targetOk && typeof s.restEndsAt === 'number';
  return {
    id: s.id ?? newId(Date.parse(s.startedAt ?? '') || Date.now()),
    programId,
    programName: s.programName ?? program?.programName ?? '',
    dayId: s.dayId,
    day,
    startedAt: s.startedAt ?? new Date().toISOString(),
    finishedAt: s.finishedAt,
    phase: s.phase === 'FINISHED' ? 'FINISHED' : resting ? 'RESTING' : 'ACTIVE_SET',
    exerciseIndex,
    setIndex: s.setIndex ?? 0,
    restEndsAt: resting ? (s.restEndsAt as number) : null,
    restSeconds: resting ? s.restSeconds ?? null : null,
    restTarget: resting ? (s.restTarget as Position) : null,
    restLabel: resting ? s.restLabel ?? null : null,
    logs,
    weights: s.weights ?? {},
    notes: s.notes ?? {},
    workoutNote: s.workoutNote,
    restOverrides: s.restOverrides ?? {},
    lastActionAt: s.lastActionAt ?? 0,
    pendingWeightFor: s.pendingWeightFor && day.exercises.some((e) => e.id === s.pendingWeightFor) ? s.pendingWeightFor : null,
    stretch: s.stretch && typeof s.stretch.endsAt === 'number' ? s.stretch : null,
    stretched: s.stretched,
    warmedUp: s.warmedUp,
    work: s.work && typeof s.work.endsAt === 'number' && s.phase === 'ACTIVE_SET' && !resting ? s.work : null,
  };
}

export function restFor(s: Session, exerciseIndex: number): number {
  const ex = s.day.exercises[exerciseIndex];
  const override = s.restOverrides[ex.id];
  return override !== undefined && override > 0 ? override : ex.restSeconds;
}

export function parseWeight(value: string | undefined | null): number | null {
  if (!value) return null;
  const n = parseFloat(value.replace(',', '.'));
  return Number.isFinite(n) && n > 0 ? n : null;
}

export function formatKg(n: number): string {
  return Number.isInteger(n) ? String(n) : String(n).replace('.', ',');
}

function nextIncompleteAfter(s: Session, from: number): number | null {
  for (let i = from + 1; i < s.day.exercises.length; i++) {
    if (s.logs[i].sets.length < s.day.exercises[i].sets) return i;
  }
  return null;
}

function positionFor(s: Session, exerciseIndex: number): Position {
  const done = s.logs[exerciseIndex].sets.length;
  return { exerciseIndex, setIndex: Math.min(done, s.day.exercises[exerciseIndex].sets - 1) };
}

function workPrep(side: 0 | 1 | 2, now: number): WorkRun {
  return { phase: 'prep', side, endsAt: now + WORK_PREP_SECONDS * 1000, total: WORK_PREP_SECONDS };
}

/** Timed exercise (plank): start its timer for the current set; otherwise make sure no timer is running. */
function autoWork(s: Session, now: number): Session {
  const ex = s.day.exercises[s.exerciseIndex];
  if (!ex.seconds || s.logs[s.exerciseIndex].sets.length >= ex.sets) return { ...s, work: null };
  return { ...s, work: workPrep(ex.sides === 2 ? 1 : 0, now) };
}

/** Logs the current set and starts the rest, or finishes the workout after the very last set. */
function completeSet(s: Session, now: number, perSetWeight?: string): Session {
  const ex = s.day.exercises[s.exerciseIndex];
  const log = s.logs[s.exerciseIndex];
  if (log.sets.length >= ex.sets) return s;
  // The weight is asked once per exercise (pendingWeightFor); a value typed for this set wins.
  const perSetKg = parseWeight(perSetWeight);
  const setLog: SetLog = {
    set: log.sets.length + 1,
    reps: ex.reps,
    weightKg: perSetKg,
    perSet: perSetKg !== null,
    completedAt: new Date(now).toISOString(),
  };
  const newLog = { ...log, sets: [...log.sets, setLog] };
  const logs = s.logs.map((l, i) => (i === s.exerciseIndex ? newLog : l));
  const exerciseDone = newLog.sets.length >= ex.sets;
  const base: Session = { ...s, logs, lastActionAt: now, pendingWeightFor: exerciseDone ? ex.id : null, work: null };
  let target: Position | null = null;
  let label: 'set' | 'exercise' | null = null;
  if (!exerciseDone) {
    target = { exerciseIndex: s.exerciseIndex, setIndex: newLog.sets.length };
    label = 'set';
  } else {
    const next = nextIncompleteAfter(base, s.exerciseIndex);
    if (next !== null) {
      target = { exerciseIndex: next, setIndex: logs[next].sets.length };
      label = 'exercise';
    }
  }
  if (!target) return { ...base, phase: 'FINISHED', finishedAt: new Date(now).toISOString(), ...NO_REST };
  const rest = restFor(s, s.exerciseIndex);
  return { ...base, phase: 'RESTING', restEndsAt: now + rest * 1000, restSeconds: rest, restTarget: target, restLabel: label };
}

/** Warm-up / cool-down: go to step `index` (a short "get ready" phase first), or finish after the last step. */
function stretchStep(s: Session, list: GuidedList, index: number, now: number): Session {
  const steps = stretchSteps(s.day, list);
  if (index >= steps.length) return list === 'warmup' ? { ...s, stretch: null, warmedUp: true } : { ...s, stretch: null, stretched: true };
  return {
    ...s,
    stretch: { list, index: Math.max(0, index), phase: 'prep', endsAt: now + STRETCH_PREP_SECONDS * 1000, total: STRETCH_PREP_SECONDS },
  };
}

/** Name of side 1 / side 2 of a two-sided item: the side to start with comes first. */
export function sideName(side: number, startSide?: Exercise['startSide']): string {
  if (side !== 1 && side !== 2) return '';
  const first = startSide === 'right' ? 'dešinė' : 'kairė';
  const second = startSide === 'right' ? 'kairė' : 'dešinė';
  return side === 1 ? first : second;
}

function lastSetTime(s: Session): string {
  let t = '';
  for (const l of s.logs) for (const st of l.sets) if (st.completedAt > t) t = st.completedAt;
  return t;
}

export function reduce(s: Session, a: Action): Session {
  const day = s.day;
  switch (a.type) {
    case 'COMPLETE_SET': {
      if (s.phase !== 'ACTIVE_SET' || s.pendingWeightFor) return s;
      if (a.now - s.lastActionAt < DOUBLE_TAP_MS) return s;
      return completeSet(s, a.now, a.perSetWeight);
    }
    case 'REST_DONE':
    case 'SKIP_REST': {
      if (s.phase !== 'RESTING' || !s.restTarget) return s;
      const next: Session = { ...s, phase: 'ACTIVE_SET', exerciseIndex: s.restTarget.exerciseIndex, setIndex: s.restTarget.setIndex, ...NO_REST, lastActionAt: a.now };
      // A timed exercise (plank) starts its own timer here: "get ready", then the hold.
      return autoWork(next, a.now);
    }
    case 'WORK_START': {
      if (s.phase !== 'ACTIVE_SET' || s.pendingWeightFor || s.work) return s;
      return autoWork(s, a.now);
    }
    case 'WORK_ADVANCE': {
      const w = s.work;
      if (!w || s.phase !== 'ACTIVE_SET' || a.now < w.endsAt - 300) return s;
      if (a.now - w.endsAt > STALE_WORK_MS) return { ...s, work: null };
      const hold = day.exercises[s.exerciseIndex].seconds ?? 30;
      // The next phase starts exactly when the previous one ended, so polling lag never stretches a hold.
      if (w.phase === 'prep') return { ...s, work: { ...w, phase: 'hold', endsAt: w.endsAt + hold * 1000, total: hold } };
      if (w.side === 1) return { ...s, work: workPrep(2, w.endsAt) };
      return completeSet(s, a.now);
    }
    case 'WORK_ADD': {
      const w = s.work;
      if (!w || w.phase !== 'hold') return s;
      return { ...s, work: { ...w, endsAt: w.endsAt + a.seconds * 1000, total: w.total + a.seconds } };
    }
    case 'WORK_STOP':
      return s.work ? { ...s, work: null } : s;
    case 'ADJUST_REST': {
      if (s.phase !== 'RESTING' || s.restEndsAt === null) return s;
      const endsAt = Math.max(a.now + 1000, s.restEndsAt + a.deltaSec * 1000);
      const total = Math.max(1, (s.restSeconds ?? 0) + a.deltaSec);
      return { ...s, restEndsAt: endsAt, restSeconds: total };
    }
    case 'PREV_EXERCISE': {
      if (s.phase !== 'ACTIVE_SET' || s.exerciseIndex === 0) return s;
      return { ...s, ...positionFor(s, s.exerciseIndex - 1), work: null };
    }
    case 'NEXT_EXERCISE': {
      if (s.phase !== 'ACTIVE_SET' || s.exerciseIndex >= day.exercises.length - 1) return s;
      return { ...s, ...positionFor(s, s.exerciseIndex + 1), work: null };
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
        ...NO_REST,
        work: null,
        finishedAt: undefined,
        lastActionAt: a.now,
        pendingWeightFor: s.pendingWeightFor === logs[bestIdx].exerciseId ? null : s.pendingWeightFor ?? null,
      };
    }
    case 'SET_WEIGHT':
      return { ...s, weights: { ...s.weights, [a.exerciseId]: a.value } };
    case 'RESOLVE_WEIGHT': {
      if (s.pendingWeightFor !== a.exerciseId) return s;
      const weights = { ...s.weights };
      if (a.value !== null && parseWeight(a.value) !== null) weights[a.exerciseId] = a.value.trim();
      return { ...s, weights, pendingWeightFor: null };
    }
    case 'SET_NOTE':
      return { ...s, notes: { ...s.notes, [a.exerciseId]: a.value } };
    case 'SET_WORKOUT_NOTE':
      return { ...s, workoutNote: a.value };
    case 'STRETCH_START': {
      const list = a.list ?? 'cooldown';
      return stretchSteps(day, list).length ? stretchStep({ ...s, work: null }, list, 0, a.now) : s;
    }
    case 'STRETCH_ADVANCE': {
      const st = s.stretch;
      if (!st || a.now < st.endsAt - 300) return s;
      const list = st.list ?? 'cooldown';
      if (st.phase === 'prep') {
        const hold = stretchSteps(day, list)[st.index]?.stretch.hold ?? 30;
        return { ...s, stretch: { ...st, phase: 'hold', endsAt: a.now + hold * 1000, total: hold } };
      }
      return stretchStep(s, list, st.index + 1, a.now);
    }
    case 'STRETCH_SKIP':
      return s.stretch ? stretchStep(s, s.stretch.list ?? 'cooldown', s.stretch.index + 1, a.now) : s;
    case 'STRETCH_BACK':
      return s.stretch ? stretchStep(s, s.stretch.list ?? 'cooldown', s.stretch.index - 1, a.now) : s;
    case 'STRETCH_ADD': {
      const st = s.stretch;
      if (!st || st.phase !== 'hold') return s;
      return { ...s, stretch: { ...st, endsAt: st.endsAt + a.seconds * 1000, total: st.total + a.seconds } };
    }
    case 'STRETCH_EXIT':
      return { ...s, stretch: null };
    case 'SWAP_VARIANT': {
      // Only before the first set of that exercise, so the logged sets always belong to one version.
      const ex = day.exercises[a.exerciseIndex];
      if (!ex?.choices || ex.choices.length < 2 || s.logs[a.exerciseIndex].sets.length > 0) return s;
      const next = withChoice(ex, (ex.choice ?? 0) + 1);
      return {
        ...s,
        day: { ...day, exercises: day.exercises.map((e, i) => (i === a.exerciseIndex ? next : e)) },
        logs: s.logs.map((l, i) => (i === a.exerciseIndex ? { exerciseId: next.id, sets: [] } : l)),
        work: a.exerciseIndex === s.exerciseIndex ? null : s.work ?? null,
      };
    }
    case 'FINISH': {
      if (s.phase === 'FINISHED') return s;
      const last = lastSetTime(s);
      const finishedAt = last && a.now - Date.parse(last) > STALE_FINISH_MS ? last : new Date(a.now).toISOString();
      return { ...s, phase: 'FINISHED', finishedAt, ...NO_REST, work: null };
    }
    case 'REOPEN': {
      if (s.phase !== 'FINISHED') return s;
      return { ...s, phase: 'ACTIVE_SET', finishedAt: undefined, ...positionFor(s, s.exerciseIndex), work: null };
    }
    default:
      return s;
  }
}

export function progress(s: Session): { done: number; planned: number; percent: number } {
  const planned = s.day.exercises.reduce((n, e) => n + e.sets, 0);
  const done = s.logs.reduce((n, l) => n + l.sets.length, 0);
  return { done, planned, percent: planned ? Math.round((done / planned) * 100) : 0 };
}

/** Sets of one exercise with the weight resolved: a weight typed for that set wins, otherwise the exercise weight. */
export function effectiveSets(s: Session, exerciseIndex: number): SetLog[] {
  const ex = s.day.exercises[exerciseIndex];
  const exerciseKg = parseWeight(s.weights[ex.id]);
  return s.logs[exerciseIndex].sets.map((st) => (st.perSet ? st : { ...st, weightKg: exerciseKg }));
}

export function toRecord(s: Session): WorkoutRecord {
  const { done, planned } = progress(s);
  const finishedAt = s.finishedAt ?? (lastSetTime(s) || s.startedAt);
  return {
    id: s.id,
    programId: s.programId,
    programName: s.programName,
    dayId: s.dayId,
    dayName: s.day.name,
    dayColor: s.day.color,
    startedAt: s.startedAt,
    finishedAt,
    durationSec: Math.max(0, Math.round((Date.parse(finishedAt) - Date.parse(s.startedAt)) / 1000)),
    totalSetsDone: done,
    totalSetsPlanned: planned,
    exercises: s.day.exercises.map((ex, i) => ({
      exerciseId: ex.id,
      name: ex.name,
      plannedSets: ex.sets,
      reps: ex.reps,
      sets: effectiveSets(s, i),
      note: s.notes[ex.id]?.trim() || undefined,
    })),
    note: s.workoutNote?.trim() || undefined,
    completed: s.phase === 'FINISHED',
    stretched: s.stretched || undefined,
    warmedUp: s.warmedUp || undefined,
    updatedAt: new Date().toISOString(),
  };
}

/** Texts for the Android notification while a warm-up or cool-down item is held. */
export function stretchTimerText(s: Session): { title: string; text: string; doneTitle: string; doneText: string } {
  const warm = s.stretch?.list === 'warmup';
  const steps = stretchSteps(s.day, warm ? 'warmup' : 'cooldown');
  const i = s.stretch?.index ?? 0;
  const cur = steps[i];
  const next = steps[i + 1];
  const sideText = (side: number) => (side ? ` (${sideName(side)})` : '');
  const nextText = next ? `Toliau: ${next.stretch.name}${sideText(next.side)}` : warm ? 'Paskutinis apšilimo pratimas' : 'Paskutinis tempimas';
  return {
    title: `${warm ? 'Apšilimas' : 'Tempimas'} · ${cur ? cur.stretch.name + sideText(cur.side) : ''}`,
    text: nextText,
    doneTitle: next ? 'Keisk' : warm ? 'Apšilimas baigtas' : 'Tempimas baigtas',
    doneText: next ? nextText : warm ? 'Laikas treniruotei' : nextText,
  };
}

/** Texts for the Android notification while a timed set (plank) is held. */
export function workTimerText(s: Session): { title: string; text: string; doneTitle: string; doneText: string } {
  const ex = s.day.exercises[s.exerciseIndex];
  const setText = `setas ${s.logs[s.exerciseIndex].sets.length + 1}/${ex.sets}`;
  const side = s.work?.side ?? 0;
  const sideText = side ? ` (${sideName(side, ex.startSide)})` : '';
  const more = side === 1;
  return {
    title: `Laikyk · ${ex.name}${sideText}`,
    text: setText,
    doneTitle: more ? 'Keisk pusę' : 'Setas atliktas',
    doneText: more ? `${ex.name} · ${sideName(2, ex.startSide)} pusė` : `${ex.name} · ${setText} · poilsis`,
  };
}

/** Last weight used per exercise (by name, so it carries across days and programs), newest first. */
export function lastWeights(history: WorkoutRecord[], excludeId?: string): Record<string, number> {
  const out: Record<string, number> = {};
  const sorted = history.filter((r) => r.id !== excludeId).sort((a, b) => b.finishedAt.localeCompare(a.finishedAt));
  for (const rec of sorted) {
    for (const ex of rec.exercises) {
      const key = exerciseKey(ex.name);
      if (out[key] !== undefined) continue;
      const withWeight = [...ex.sets].reverse().find((st) => st.weightKg !== null);
      if (withWeight && withWeight.weightKg !== null) out[key] = withWeight.weightKg;
    }
  }
  return out;
}

/** How an exercise went the last time it was done. */
export interface LastPerformance {
  /** When that workout ended (ISO). */
  date: string;
  /** Weight of each set (null = not entered). */
  weights: (number | null)[];
}

/** The last time each exercise was done (by name, across days and programs), whether or not a weight was entered. */
export function lastPerformance(history: WorkoutRecord[], excludeId?: string): Record<string, LastPerformance> {
  const out: Record<string, LastPerformance> = {};
  const sorted = history.filter((r) => r.id !== excludeId).sort((a, b) => b.finishedAt.localeCompare(a.finishedAt));
  for (const rec of sorted) {
    for (const ex of rec.exercises) {
      const key = exerciseKey(ex.name);
      if (out[key] || ex.sets.length === 0) continue;
      out[key] = { date: rec.finishedAt, weights: ex.sets.map((st) => st.weightKg) };
    }
  }
  return out;
}

/** "10-14" */
export function formatShortDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  return String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

export function lastDoneByDay(history: WorkoutRecord[], programId: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const r of history) {
    if ((r.programId ?? DEFAULT_PROGRAM_ID) !== programId) continue;
    if (!out[r.dayId] || r.finishedAt > out[r.dayId]) out[r.dayId] = r.finishedAt;
  }
  return out;
}

/** Texts for the Android notifications during a rest. */
export function restTimerText(s: Session): { title: string; text: string; doneTitle: string; doneText: string } {
  const t = s.restTarget;
  const cur = s.day.exercises[s.exerciseIndex];
  if (!t) return { title: 'Poilsis', text: '', doneTitle: 'Poilsis baigėsi', doneText: '' };
  if (s.restLabel === 'set') {
    const setText = `setas ${t.setIndex + 1}/${cur.sets}`;
    return { title: `Poilsis · ${cur.name}`, text: `Toliau ${setText}`, doneTitle: 'Poilsis baigėsi', doneText: `${cur.name} · ${setText}` };
  }
  const next = s.day.exercises[t.exerciseIndex];
  return {
    title: 'Poilsis prieš kitą pratimą',
    text: `Toliau: ${next.name} · ${next.sets} × ${next.reps}`,
    doneTitle: 'Poilsis baigėsi',
    doneText: `Toliau: ${next.name}`,
  };
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
  return (
    d.toLocaleDateString('lt-LT', { year: 'numeric', month: '2-digit', day: '2-digit' }) +
    ' ' +
    d.toLocaleTimeString('lt-LT', { hour: '2-digit', minute: '2-digit' })
  );
}

export function formatWeight(kg: number | null): string {
  if (kg === null) return '—';
  return formatKg(Math.round(kg * 100) / 100) + ' kg';
}
