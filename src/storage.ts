import type { Session, Settings, WorkoutRecord } from './types';
import { mirrorToNative } from './native';

const KEYS = {
  session: 'kyokushin.session.v1',
  history: 'kyokushin.history.v1',
  rest: 'kyokushin.rest.v1',
  settings: 'kyokushin.settings.v1',
};

export const STORAGE_KEYS = Object.values(KEYS);

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
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

export const storage = {
  loadSession: () => read<Session | null>(KEYS.session, null),
  saveSession: (s: Session | null) => write(KEYS.session, s),
  loadHistory: () => read<WorkoutRecord[]>(KEYS.history, []),
  saveHistory: (h: WorkoutRecord[]) => write(KEYS.history, h),
  loadRestOverrides: () => read<Record<string, number>>(KEYS.rest, {}),
  saveRestOverrides: (r: Record<string, number>) => write(KEYS.rest, r),
  loadSettings: () => read<Settings>(KEYS.settings, { sound: true, vibrate: true }),
  saveSettings: (s: Settings) => write(KEYS.settings, s),
};
