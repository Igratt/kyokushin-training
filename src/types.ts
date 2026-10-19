export type DayId = string;

export interface Exercise {
  id: string;
  name: string;
  sets: number;
  reps: string;
  restSeconds: number;
  /** Timed exercise (plank etc.): seconds to hold per set. The app runs that timer itself after the rest. */
  seconds?: number;
  /** 2 = the hold is done on the left and then on the right side (side plank). */
  sides?: 1 | 2;
  /** One-sided exercise: start with this (weaker) side, then do the same reps with the other one. */
  startSide?: 'left' | 'right';
  image?: string;
  description?: string;
  focus?: string;
  /** Short label of a variant, e.g. "su guma". */
  tag?: string;
  /** Other ways to do the same exercise. The app alternates between the base and its variants. */
  variants?: Exercise[];
  /** Inside a workout: every version of this exercise (base first) and which one is being done. */
  choices?: Exercise[];
  choice?: number;
}

/** A stretch for the cool-down after the workout. */
export interface Stretch {
  id: string;
  name: string;
  /** Hold time in seconds, per side. */
  hold: number;
  /** 2 = done on the left and then the right side. */
  sides: 1 | 2;
  image?: string;
  description?: string;
  /** Why it matters for karate / the gym. */
  focus?: string;
}

export interface Day {
  id: DayId;
  name: string;
  subtitle?: string;
  /** Accent colour of the day (A blue, B orange, C green, other days from a palette). */
  color: string;
  exercises: Exercise[];
  /** Guided warm-up before the workout (hip mobility), run like the cool-down. */
  warmup?: Stretch[];
  stretches?: Stretch[];
}

/** The guided timer lists of a day: the warm-up before and the cool-down after the workout. */
export type GuidedList = 'warmup' | 'cooldown';

/** Progress of the warm-up or cool-down. Like the rest timer, it runs on an absolute end timestamp. */
export interface StretchRun {
  /** Which list is running. Sessions saved before the warm-up existed have none: the cool-down. */
  list?: GuidedList;
  /** Index into stretchSteps(day, list): every side of every item is one step. */
  index: number;
  phase: 'prep' | 'hold';
  endsAt: number;
  /** Length of the current phase in seconds (for the ring). */
  total: number;
}

/** Timer of a timed set (plank): "get ready" → hold (→ other side); the set completes itself at the end. */
export interface WorkRun {
  phase: 'prep' | 'hold';
  /** 0 = one block, 1 = left side, 2 = right side. */
  side: 0 | 1 | 2;
  endsAt: number;
  /** Length of the current phase in seconds (for the ring). */
  total: number;
}

export interface Program {
  id: string;
  programName: string;
  goal?: string;
  focus?: string;
  days: Day[];
  /** Built into the app (src/data/programs) or imported from a file on this phone. */
  source: 'builtin' | 'imported';
}

export interface SetLog {
  set: number;
  reps: string;
  weightKg: number | null;
  /** True when the weight was typed for this specific set; otherwise the exercise-level weight applies. */
  perSet?: boolean;
  completedAt: string;
}

export interface ExerciseLog {
  exerciseId: string;
  sets: SetLog[];
}

export type Phase = 'ACTIVE_SET' | 'RESTING' | 'FINISHED';

export interface Position {
  exerciseIndex: number;
  setIndex: number;
}

/** The whole live workout. Persisted on every change so a refresh or a locked phone loses nothing. */
export interface Session {
  id: string;
  programId: string;
  programName: string;
  dayId: DayId;
  /** Snapshot of the day as it was at the start, so later program changes never break a running workout. */
  day: Day;
  startedAt: string;
  finishedAt?: string;
  phase: Phase;
  exerciseIndex: number;
  setIndex: number;
  /** Absolute timestamp (ms) when the current rest ends. The timer is derived from it, never from a counter. */
  restEndsAt: number | null;
  restSeconds: number | null;
  restTarget: Position | null;
  restLabel: 'set' | 'exercise' | null;
  logs: ExerciseLog[];
  /** Confirmed weight per exercise id, as typed (so "72,5" stays as typed). */
  weights: Record<string, string>;
  notes: Record<string, string>;
  workoutNote?: string;
  restOverrides: Record<string, number>;
  lastActionAt: number;
  /** Exercise whose "what weight did you use?" dialog is open (set right after its last set). */
  pendingWeightFor?: string | null;
  /** Cool-down in progress (null when not stretching). */
  stretch?: StretchRun | null;
  /** The cool-down was done to the end. */
  stretched?: boolean;
  /** The warm-up was done to the end. */
  warmedUp?: boolean;
  /** Running timer of a timed set (null when none). */
  work?: WorkRun | null;
}

export interface RecordExercise {
  exerciseId: string;
  name: string;
  plannedSets: number;
  reps: string;
  sets: SetLog[];
  note?: string;
}

export interface WorkoutRecord {
  id: string;
  programId?: string;
  programName?: string;
  dayId: DayId;
  dayName?: string;
  dayColor?: string;
  startedAt: string;
  finishedAt: string;
  durationSec: number;
  totalSetsDone: number;
  totalSetsPlanned: number;
  exercises: RecordExercise[];
  note?: string;
  /** False while the workout is still running (it is saved after every set). Older records have no flag. */
  completed?: boolean;
  /** The cool-down stretches were done. */
  stretched?: boolean;
  /** The warm-up was done. */
  warmedUp?: boolean;
  updatedAt?: string;
}

export interface Settings {
  sound: boolean;
  vibrate: boolean;
  programId?: string;
}
