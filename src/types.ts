export type DayId = string;

export interface Exercise {
  id: string;
  name: string;
  sets: number;
  reps: string;
  restSeconds: number;
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

export interface Day {
  id: DayId;
  name: string;
  subtitle?: string;
  /** Accent colour of the day (A blue, B orange, C green, other days from a palette). */
  color: string;
  exercises: Exercise[];
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
  updatedAt?: string;
}

export interface Settings {
  sound: boolean;
  vibrate: boolean;
  programId?: string;
}
