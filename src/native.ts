import { Capacitor, registerPlugin } from '@capacitor/core';
import { Preferences } from '@capacitor/preferences';

/** True inside the Android app, false in the browser / PWA. */
export const isNative = Capacitor.isNativePlatform();

/* ---- the app's own storage (Capacitor Preferences): survives everything except uninstalling ---- */

export async function nativeGet(key: string): Promise<string | null> {
  if (!isNative) return null;
  try {
    return (await Preferences.get({ key })).value;
  } catch {
    return null;
  }
}

/** Mirror a localStorage write into the app's own storage (fire and forget). */
export function mirrorToNative(key: string, value: string | null): void {
  if (!isNative) return;
  const op = value === null ? Preferences.remove({ key }) : Preferences.set({ key, value });
  op.catch(() => undefined);
}

/* ---- native rest timer (APK built 2026-10-11 or later) ---- */

export interface RestTimerOptions {
  endAt: number;
  title: string;
  text: string;
  doneTitle: string;
  doneText: string;
  sound: boolean;
  vibrate: boolean;
}

interface RestTimerPlugin {
  prepare(): Promise<void>;
  start(options: RestTimerOptions): Promise<void>;
  cancel(): Promise<void>;
}

const RestTimerNative = registerPlugin<RestTimerPlugin>('RestTimer');

/**
 * When available, the Android side shows the countdown in the notification shade and plays the end-of-rest
 * beep itself, also while the app is hidden. Older APKs and the browser fall back to the in-page beep.
 */
export const nativeTimer = isNative && Capacitor.isPluginAvailable('RestTimer');

export const restTimer = {
  prepare: () => (nativeTimer ? RestTimerNative.prepare().catch(() => undefined) : Promise.resolve()),
  start: (o: RestTimerOptions) => (nativeTimer ? RestTimerNative.start({ ...o, endAt: Math.round(o.endAt) }).catch(() => undefined) : Promise.resolve()),
  cancel: () => (nativeTimer ? RestTimerNative.cancel().catch(() => undefined) : Promise.resolve()),
};

/* ---- files out ---- */

const nativeShare = isNative && Capacitor.isPluginAvailable('Share') && Capacitor.isPluginAvailable('Filesystem');

/** Android app: share sheet (Drive, OneDrive, Files…). Browser: a normal download. */
export async function saveJsonFile(name: string, data: string): Promise<void> {
  if (nativeShare) {
    const { Directory, Encoding, Filesystem } = await import('@capacitor/filesystem');
    const { Share } = await import('@capacitor/share');
    const file = await Filesystem.writeFile({ path: name, data, directory: Directory.Cache, encoding: Encoding.UTF8 });
    await Share.share({ title: name, files: [file.uri] });
    return;
  }
  const blob = new Blob([data], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a);
  a.click();
  window.setTimeout(() => {
    URL.revokeObjectURL(a.href);
    a.remove();
  }, 1000);
}
