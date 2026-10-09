export type DayId = 'A' | 'B' | 'C';

export interface Exercise {
  id: string;
  name: string;
  sets: number;
  reps: string;
  restSeconds: number;
  image: string;
  description: string;
  focus: string;
}

export interface Day {
  id: DayId;
  name: string;
  subtitle: string;
  exercises: Exercise[];
}

export interface Program {
  programName: string;
  goal: string;
  days: Day[];
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

/** The whole live workout. Persisted to localStorage on every change so a refresh or a locked phone loses nothing. */
export interface Session {
  dayId: DayId;
  startedAt: string;
  finishedAt?: string;
  phase: Phase;
  exerciseIndex: number;
  setIndex: number;
  /** Absolute timestamp (ms) when the current rest ends. Timer is derived from this, never from a counter. */
  restEndsAt: number | null;
  restSeconds: number | null;
  restTarget: Position | null;
  restLabel: 'set' | 'exercise' | null;
  logs: ExerciseLog[];
  /** Weight input text per exercise id (string so "72,5" stays as typed). */
  weights: Record<string, string>;
  notes: Record<string, string>;
  restOverrides: Record<string, number>;
  lastActionAt: number;
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
  dayId: DayId;
  startedAt: string;
  finishedAt: string;
  durationSec: number;
  totalSetsDone: number;
  totalSetsPlanned: number;
  exercises: RecordExercise[];
  note?: string;
}

export interface Settings {
  sound: boolean;
  vibrate: boolean;
}
