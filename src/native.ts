import { Capacitor } from '@capacitor/core';
import { Preferences } from '@capacitor/preferences';

/** True inside the packaged Android app, false in the browser / PWA. */
export const isNative = Capacitor.isNativePlatform();

/**
 * In the Android app the durable store is Capacitor Preferences (the app's own storage, untouched by
 * browser data clearing). localStorage stays the synchronous cache the app reads at startup, so on boot
 * every known key is copied from Preferences into localStorage before React renders.
 */
export async function hydrateStorage(keys: string[]): Promise<void> {
  if (!isNative) return;
  for (const key of keys) {
    try {
      const { value } = await Preferences.get({ key });
      if (value !== null) localStorage.setItem(key, value);
    } catch {
      /* keep whatever localStorage already has */
    }
  }
}

/** Mirror a localStorage write into the native store (fire and forget). */
export function mirrorToNative(key: string, value: string | null): void {
  if (!isNative) return;
  const op = value === null ? Preferences.remove({ key }) : Preferences.set({ key, value });
  op.catch(() => undefined);
}
