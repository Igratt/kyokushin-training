import type { Day, Exercise, Program, Stretch } from '../types';

/*
 * Training programs. Every JSON file in ./programs is a built-in program, in the same format as the
 * original workout_data.json (programName, goal, days[] with exercises[]). To add a program, put a new
 * JSON file into src/data/programs and run `npm run deploy`: it appears under Nustatymai → Programa.
 * Programs can also be imported from a .json file on the phone; those live only on that phone.
 */

export const DEFAULT_PROGRAM_ID = 'kyokushin-mix';

const files = import.meta.glob('./programs/*.json', { eager: true, import: 'default' }) as Record<string, unknown>;

const DAY_COLORS: Record<string, string> = { A: '#3B82F6', B: '#F97316', C: '#22C55E' };
const PALETTE = ['#3B82F6', '#F97316', '#22C55E', '#A855F7', '#EAB308', '#EC4899', '#14B8A6'];

export function dayColor(dayId: string, index: number): string {
  return DAY_COLORS[dayId.trim().toUpperCase()] ?? PALETTE[index % PALETTE.length];
}

/** The same exercise in another day or program shares its last used weight. */
export function exerciseKey(name: string): string {
  return name.trim().toLowerCase().replace(/\s+/g, ' ');
}

/** Lithuanian plural: plural(4, 'setas', 'setai', 'setų') → "setai". */
export function plural(n: number, one: string, few: string, many: string): string {
  const d = n % 10;
  const t = n % 100;
  if (d === 1 && t !== 11) return one;
  if (d >= 2 && (t < 11 || t > 19)) return few;
  return many;
}

function slug(value: string): string {
  const s = value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return s.slice(0, 40) || 'programa';
}

function fail(message: string): never {
  throw new Error(message);
}

function toNumber(v: unknown): number {
  if (typeof v === 'number') return v;
  if (typeof v === 'string') return parseFloat(v.replace(',', '.'));
  return NaN;
}

function text(v: unknown): string | undefined {
  return typeof v === 'string' && v.trim() ? v.trim() : undefined;
}

function image(v: unknown): string | undefined {
  const s = text(v);
  if (!s) return undefined;
  // The photos from the PDF ship as WebP; program files may still say .png.
  return /^assets\/[\w-]+\.png$/i.test(s) ? s.replace(/\.png$/i, '.webp') : s;
}

function normalizeExercise(e: unknown, label: string, fallbackId: string, ids: Set<string>, allowVariants: boolean): Exercise {
  if (!e || typeof e !== 'object') fail(`${label} neteisingas.`);
  const er = e as Record<string, unknown>;
  const name = text(er.name) ?? fail(`${label} be pavadinimo („name“).`);
  const sets = Math.round(toNumber(er.sets));
  if (!(sets >= 1 && sets <= 20)) fail(`„${name}“: „sets“ turi būti skaičius nuo 1 iki 20.`);
  const reps = typeof er.reps === 'number' ? String(er.reps) : text(er.reps) ?? fail(`„${name}“: trūksta „reps“.`);
  const rest = er.restSeconds === undefined ? 90 : Math.round(toNumber(er.restSeconds));
  if (!(rest >= 0 && rest <= 900)) fail(`„${name}“: „restSeconds“ turi būti nuo 0 iki 900.`);
  let id = text(er.id) ?? fallbackId;
  while (ids.has(id)) id += '_';
  ids.add(id);
  let variants: Exercise[] | undefined;
  if (allowVariants && Array.isArray(er.variants) && er.variants.length > 0) {
    if (er.variants.length > 5) fail(`„${name}“: daugiausia 5 variantai.`);
    variants = (er.variants as unknown[]).map((v, vi) => normalizeExercise(v, `„${name}“ ${vi + 1}-asis variantas`, `${id}v${vi + 1}`, ids, false));
  }
  return {
    id,
    name,
    sets,
    reps,
    restSeconds: rest,
    image: image(er.image),
    description: text(er.description),
    focus: text(er.focus),
    tag: text(er.tag),
    variants,
  };
}

function normalizeStretch(e: unknown, label: string, fallbackId: string): Stretch {
  if (!e || typeof e !== 'object') fail(`${label} neteisingas.`);
  const er = e as Record<string, unknown>;
  const name = text(er.name) ?? fail(`${label} be pavadinimo („name“).`);
  const hold = er.hold === undefined ? 30 : Math.round(toNumber(er.hold));
  if (!(hold >= 5 && hold <= 300)) fail(`„${name}“: „hold“ turi būti nuo 5 iki 300 sekundžių.`);
  const sides = er.sides === undefined ? 1 : Math.round(toNumber(er.sides));
  if (sides !== 1 && sides !== 2) fail(`„${name}“: „sides“ turi būti 1 arba 2.`);
  return {
    id: text(er.id) ?? fallbackId,
    name,
    hold,
    sides: sides as 1 | 2,
    image: image(er.image),
    description: text(er.description),
    focus: text(er.focus),
  };
}

/** Every side of every cool-down stretch, in order. side: 0 = whole body, 1 = left, 2 = right. */
export function stretchSteps(day: Day): { stretch: Stretch; side: 0 | 1 | 2 }[] {
  const out: { stretch: Stretch; side: 0 | 1 | 2 }[] = [];
  for (const st of day.stretches ?? []) {
    if (st.sides === 2) out.push({ stretch: st, side: 1 }, { stretch: st, side: 2 });
    else out.push({ stretch: st, side: 0 });
  }
  return out;
}

/** Seconds of preparation before each hold. */
export const STRETCH_PREP_SECONDS = 5;

export function stretchMinutes(day: Day): number {
  const seconds = stretchSteps(day).reduce((n, s) => n + s.stretch.hold + STRETCH_PREP_SECONDS, 0);
  return Math.max(1, Math.round(seconds / 60));
}

/** One version of an exercise without the variant bookkeeping. */
function plain(ex: Exercise): Exercise {
  return {
    id: ex.id,
    name: ex.name,
    sets: ex.sets,
    reps: ex.reps,
    restSeconds: ex.restSeconds,
    image: ex.image,
    description: ex.description,
    focus: ex.focus,
    tag: ex.tag,
  };
}

/** All ways to do an exercise: the base first, then its variants. */
export function versionsOf(ex: Exercise): Exercise[] {
  if (ex.choices && ex.choices.length > 0) return ex.choices;
  return [plain(ex), ...(ex.variants ?? []).map(plain)];
}

/**
 * Which version of each exercise to use: they alternate every time the day is done again
 * (rotation = how many times this day was done before), so the body never gets used to one method.
 */
export function pickChoices(day: Day, rotation: number): number[] {
  return day.exercises.map((ex) => {
    const n = versionsOf(ex).length;
    return n > 1 ? rotation % n : 0;
  });
}

/** The exercise as done in a workout: the chosen version, remembering the others so it can be swapped. */
export function withChoice(ex: Exercise, choice: number): Exercise {
  const versions = versionsOf(ex);
  if (versions.length < 2) return plain(ex);
  const c = ((choice % versions.length) + versions.length) % versions.length;
  return { ...versions[c], choices: versions, choice: c };
}

/** Validates a program (a built-in file or one the user imports) and fills in defaults. Throws with a Lithuanian message. */
export function normalizeProgram(raw: unknown, source: Program['source']): Program {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) fail('Failas nėra programa: tikėtasi JSON objekto su „days“.');
  const r = raw as Record<string, unknown>;
  if (!Array.isArray(r.days) || r.days.length === 0) fail('Programoje nėra dienų („days“ sąrašo).');
  if (r.days.length > 7) fail('Programoje gali būti daugiausia 7 dienos.');
  const programName = text(r.programName) ?? text(r.name) ?? 'Programa';
  const dayIds = new Set<string>();
  const days: Day[] = (r.days as unknown[]).map((d, di) => {
    if (!d || typeof d !== 'object') fail(`${di + 1}-oji diena neteisinga.`);
    const dr = d as Record<string, unknown>;
    const id = text(dr.id) ?? String.fromCharCode(65 + di);
    if (dayIds.has(id)) fail(`Dienos ID „${id}“ kartojasi.`);
    dayIds.add(id);
    if (!Array.isArray(dr.exercises) || dr.exercises.length === 0) fail(`Dienoje ${id} nėra pratimų („exercises“).`);
    if (dr.exercises.length > 20) fail(`Dienoje ${id} per daug pratimų (daugiausia 20).`);
    const exIds = new Set<string>();
    const exercises: Exercise[] = (dr.exercises as unknown[]).map((e, ei) =>
      normalizeExercise(e, `Dienos ${id} ${ei + 1}-asis pratimas`, `${id}${ei + 1}`, exIds, true),
    );
    let stretches: Stretch[] | undefined;
    if (Array.isArray(dr.stretches) && dr.stretches.length > 0) {
      if (dr.stretches.length > 15) fail(`Dienoje ${id} per daug tempimo pratimų (daugiausia 15).`);
      stretches = (dr.stretches as unknown[]).map((st, si) => normalizeStretch(st, `Dienos ${id} ${si + 1}-asis tempimas`, `${id}S${si + 1}`));
    }
    return { id, name: text(dr.name) ?? `${id} DIENA`, subtitle: text(dr.subtitle), color: dayColor(id, di), exercises, stretches };
  });
  return { id: text(r.id) ?? slug(programName), programName, goal: text(r.goal), focus: text(r.focus), days, source };
}

export const BUILTIN_PROGRAMS: Program[] = Object.keys(files)
  .flatMap((path) => {
    try {
      return [normalizeProgram(files[path], 'builtin')];
    } catch (e) {
      console.error('Netinkama programa', path, e);
      return [];
    }
  })
  .sort((a, b) => (a.id === DEFAULT_PROGRAM_ID ? -1 : b.id === DEFAULT_PROGRAM_ID ? 1 : a.programName.localeCompare(b.programName, 'lt')));

export function allPrograms(imported: Program[]): Program[] {
  const builtinIds = new Set(BUILTIN_PROGRAMS.map((p) => p.id));
  return [...BUILTIN_PROGRAMS, ...imported.filter((p) => !builtinIds.has(p.id))];
}

export function findProgram(programs: Program[], id: string | undefined): Program {
  return programs.find((p) => p.id === id) ?? programs.find((p) => p.id === DEFAULT_PROGRAM_ID) ?? programs[0];
}

export function programStats(p: Program): string {
  const exercises = p.days.reduce((n, d) => n + d.exercises.length, 0);
  return `${p.days.length} ${plural(p.days.length, 'diena', 'dienos', 'dienų')} · ${exercises} ${plural(exercises, 'pratimas', 'pratimai', 'pratimų')}`;
}
