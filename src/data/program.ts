import raw from './workout_data.json';
import type { Day, DayId, Program } from '../types';

// workout_data.json is the single source of truth for the program. Only the image
// paths are rewritten: the PDF photos were saved as compressed WebP under public/assets.
const program = raw as unknown as Program;

export const PROGRAM_NAME = program.programName;
export const PROGRAM_GOAL = program.goal;

export const DAYS: Day[] = program.days.map((d) => ({
  ...d,
  exercises: d.exercises.map((e) => ({ ...e, image: e.image.replace(/\.png$/i, '.webp') })),
}));

export function getDay(id: DayId): Day {
  const day = DAYS.find((d) => d.id === id);
  if (!day) throw new Error('Nežinoma diena: ' + id);
  return day;
}

export const DAY_COLORS: Record<DayId, string> = { A: '#3B82F6', B: '#F97316', C: '#22C55E' };

/** Power / bodyweight moves where a weight is optional: the kg field starts collapsed. */
export const OPTIONAL_WEIGHT = new Set(['A1', 'A5', 'A7', 'A9', 'B1', 'B6', 'B9', 'C1', 'C6', 'C8', 'C9']);
