import type { Program, Session, Settings, WorkoutRecord } from './types';
import { DEFAULT_PROGRAM_ID, normalizeProgram } from './data/programs';
import { isNative, mirrorToNative, nativeGet } from './native';

export const KEYS = {
  session: 'kyokushin.session.v1',
  history: 'kyokushin.history.v1',
  rest: 'kyokushin.rest.v1',
  settings: 'kyokushin.settings.v1',
  programs: 'kyokushin.programs.v1',
};

function parse<T>(raw: string | null | undefined, fallback: T): T {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function read<T>(key: string, fallback: T): T {
  try {
    return parse(localStorage.getItem(key), fallback);
  } catch {
    return fallback;
  }
}

function write(key: string, value: unknown): boolean {
  try {
    if (value === null || value === undefined) {
      localStorage.removeItem(key);
      mirrorToNative(key, null);
    } else {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);
      mirrorToNative(key, serialized);
    }
    return true;
  } catch {
    return false;
  }
}

function asArray<T>(v: unknown): T[] {
  return Array.isArray(v) ? (v as T[]) : [];
}

function recordTime(r: WorkoutRecord): string {
  return r.updatedAt ?? r.finishedAt ?? '';
}

/** Union of two history copies by id; for the same workout the most recently updated copy wins. */
export function mergeHistory(a: WorkoutRecord[], b: WorkoutRecord[]): WorkoutRecord[] {
  const byId = new Map<string, WorkoutRecord>();
  for (const r of [...a, ...b]) {
    if (!r || typeof r !== 'object' || !r.id || !Array.isArray(r.exercises) || typeof r.finishedAt !== 'string') continue;
    const cur = byId.get(r.id);
    if (!cur || recordTime(r) > recordTime(cur)) byId.set(r.id, r);
  }
  return [...byId.values()].sort((x, y) => y.finishedAt.localeCompare(x.finishedAt));
}

export function upsertRecord(history: WorkoutRecord[], rec: WorkoutRecord): WorkoutRecord[] {
  return [rec, ...history.filter((r) => r.id !== rec.id)].sort((x, y) => y.finishedAt.localeCompare(x.finishedAt));
}

function loadPrograms(): Program[] {
  return asArray<unknown>(read(KEYS.programs, [])).flatMap((p) => {
    try {
      return [normalizeProgram(p, 'imported')];
    } catch {
      return [];
    }
  });
}

export const storage = {
  loadSession: () => read<unknown>(KEYS.session, null),
  saveSession: (s: Session | null) => write(KEYS.session, s),
  loadHistory: () => mergeHistory(asArray<WorkoutRecord>(read(KEYS.history, [])), []),
  saveHistory: (h: WorkoutRecord[]) => write(KEYS.history, h),
  /** Keys are "programId/exerciseId"; older versions stored bare exercise ids of the default program. */
  loadRestOverrides: () => {
    const raw = read<Record<string, unknown>>(KEYS.rest, {});
    const out: Record<string, number> = {};
    for (const [k, v] of Object.entries(raw)) if (typeof v === 'number') out[k.includes('/') ? k : `${DEFAULT_PROGRAM_ID}/${k}`] = v;
    return out;
  },
  saveRestOverrides: (r: Record<string, number>) => write(KEYS.rest, r),
  loadSettings: (): Settings => ({ sound: true, vibrate: true, ...read<Partial<Settings>>(KEYS.settings, {}) }),
  saveSettings: (s: Settings) => write(KEYS.settings, s),
  loadPrograms,
  savePrograms: (p: Program[]) => write(KEYS.programs, p),
};

/**
 * Android app, before the first render: merge the app's own storage with the WebView copy.
 * History and imported programs are united, so neither copy can ever wipe the other.
 */
export async function hydrate(): Promise<void> {
  if (!isNative) return;
  const [nHistory, nSession, nRest, nSettings, nPrograms] = await Promise.all(
    [KEYS.history, KEYS.session, KEYS.rest, KEYS.settings, KEYS.programs].map((k) => nativeGet(k)),
  );
  write(KEYS.history, mergeHistory(asArray(parse(nHistory, [])), asArray(read(KEYS.history, []))));

  const a = parse<Session | null>(nSession, null);
  const b = read<Session | null>(KEYS.session, null);
  write(KEYS.session, !a ? b : !b ? a : (b.lastActionAt ?? 0) > (a.lastActionAt ?? 0) ? b : a);

  const programs = new Map<string, unknown>();
  for (const p of [...asArray<{ id?: string }>(read(KEYS.programs, [])), ...asArray<{ id?: string }>(parse(nPrograms, []))]) {
    if (p && typeof p.id === 'string') programs.set(p.id, p);
  }
  write(KEYS.programs, [...programs.values()]);

  if (nRest !== null) write(KEYS.rest, parse(nRest, {}));
  if (nSettings !== null) write(KEYS.settings, parse(nSettings, {}));
}
