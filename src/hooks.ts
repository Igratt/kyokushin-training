import { useCallback, useEffect, useRef, useState } from 'react';
import type { Settings } from './types';

/** Re-renders on an interval while `active`, and immediately when the tab becomes visible again. */
export function useNow(active: boolean, intervalMs = 250): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!active) return;
    setNow(Date.now());
    const id = window.setInterval(() => setNow(Date.now()), intervalMs);
    const wake = () => setNow(Date.now());
    document.addEventListener('visibilitychange', wake);
    window.addEventListener('focus', wake);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', wake);
      window.removeEventListener('focus', wake);
    };
  }, [active, intervalMs]);
  return now;
}

type WakeLockSentinel = { release: () => Promise<void>; addEventListener?: (t: string, cb: () => void) => void };
type NavigatorWithWakeLock = Navigator & { wakeLock?: { request: (type: 'screen') => Promise<WakeLockSentinel> } };

/** Keeps the screen on during a workout where the browser supports it; silently does nothing elsewhere. */
export function useWakeLock(enabled: boolean): void {
  const lockRef = useRef<WakeLockSentinel | null>(null);
  useEffect(() => {
    const nav = navigator as NavigatorWithWakeLock;
    if (!enabled || !nav.wakeLock) return;
    let cancelled = false;
    const acquire = async () => {
      try {
        if (document.visibilityState !== 'visible') return;
        const lock = await nav.wakeLock!.request('screen');
        if (cancelled) {
          lock.release().catch(() => undefined);
          return;
        }
        lockRef.current = lock;
      } catch {
        /* denied or unsupported: nothing to do */
      }
    };
    const onVisible = () => {
      if (document.visibilityState === 'visible') acquire();
    };
    acquire();
    document.addEventListener('visibilitychange', onVisible);
    return () => {
      cancelled = true;
      document.removeEventListener('visibilitychange', onVisible);
      lockRef.current?.release().catch(() => undefined);
      lockRef.current = null;
    };
  }, [enabled]);
}

type BeforeInstallPromptEvent = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }> };

export function useInstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null);
  const [installed, setInstalled] = useState(false);
  useEffect(() => {
    const onPrompt = (e: Event) => {
      e.preventDefault();
      setDeferred(e as BeforeInstallPromptEvent);
    };
    const onInstalled = () => {
      setInstalled(true);
      setDeferred(null);
    };
    window.addEventListener('beforeinstallprompt', onPrompt);
    window.addEventListener('appinstalled', onInstalled);
    return () => {
      window.removeEventListener('beforeinstallprompt', onPrompt);
      window.removeEventListener('appinstalled', onInstalled);
    };
  }, []);
  const isStandalone =
    window.matchMedia('(display-mode: standalone)').matches || (navigator as Navigator & { standalone?: boolean }).standalone === true;
  const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const promptInstall = useCallback(async () => {
    if (!deferred) return;
    await deferred.prompt();
    try {
      await deferred.userChoice;
    } finally {
      setDeferred(null);
    }
  }, [deferred]);
  return { canInstall: !!deferred && !installed, promptInstall, isIOS, isStandalone, installed };
}

/* One audio context for the whole app: browsers only start it from a user gesture, so any tap
   (set done, start stretching) primes it and every screen can beep afterwards. */
let sharedCtx: AudioContext | null = null;

export function primeAudio(): void {
  try {
    const Ctx = window.AudioContext || (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Ctx) return;
    if (!sharedCtx) sharedCtx = new Ctx();
    if (sharedCtx.state === 'suspended') sharedCtx.resume().catch(() => undefined);
  } catch {
    /* no audio */
  }
}

/**
 * Alarm beeps. `prime()` is called on a tap (e.g. "set done") and `fire()` later plays the beeps.
 */
export function useAlarm() {
  const ctxRef = { get current() { return sharedCtx; } };
  const prime = useCallback(primeAudio, []);
  /** kind: 'rest' = full end-of-rest alarm, 'short' = quick double beep (end of a stretch), 'tick' = one soft beep (start of a hold). */
  const fire = useCallback((settings: Settings, kind: 'rest' | 'short' | 'tick' = 'rest') => {
    if (settings.vibrate && 'vibrate' in navigator && kind !== 'tick') {
      try {
        navigator.vibrate(kind === 'rest' ? [400, 150, 400, 150, 900] : [180, 100, 180]);
      } catch {
        /* ignore */
      }
    }
    if (settings.sound && ctxRef.current && kind !== 'rest') {
      try {
        const ctx = ctxRef.current;
        const t0 = ctx.currentTime;
        const LEVEL = kind === 'tick' ? 0.3 : 0.5;
        const offsets = kind === 'tick' ? [0] : [0, 0.2];
        for (const o of offsets) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'square';
          osc.frequency.value = kind === 'tick' ? 880 : 1318;
          gain.gain.setValueAtTime(0.0001, t0 + o);
          gain.gain.exponentialRampToValueAtTime(LEVEL, t0 + o + 0.01);
          gain.gain.exponentialRampToValueAtTime(0.0001, t0 + o + 0.13);
          osc.connect(gain).connect(ctx.destination);
          osc.start(t0 + o);
          osc.stop(t0 + o + 0.16);
        }
      } catch {
        /* ignore */
      }
      return;
    }
    if (settings.sound && ctxRef.current) {
      try {
        const ctx = ctxRef.current;
        const t0 = ctx.currentTime;
        // Gym alarm: three short beeps and a long one, played twice. Level 0.55 (was 0.95, "a bit quieter").
        // The Android app plays the same pattern natively (res/raw/rest_end.wav), also in the background.
        const LEVEL = 0.55;
        const beep = (at: number, freq: number, dur: number) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'square';
          osc.frequency.value = freq;
          gain.gain.setValueAtTime(0.0001, at);
          gain.gain.exponentialRampToValueAtTime(LEVEL, at + 0.015);
          gain.gain.setValueAtTime(LEVEL, at + dur - 0.04);
          gain.gain.exponentialRampToValueAtTime(0.0001, at + dur);
          osc.connect(gain).connect(ctx.destination);
          osc.start(at);
          osc.stop(at + dur + 0.05);
        };
        for (const base of [0, 2.0]) {
          [0, 0.32, 0.64].forEach((o) => beep(t0 + base + o, 1046, 0.24));
          beep(t0 + base + 1.0, 1318, 0.7);
        }
      } catch {
        /* ignore */
      }
    }
  }, []);
  return { prime, fire };
}

export function useFullscreen() {
  const [isFull, setIsFull] = useState(() => !!document.fullscreenElement);
  useEffect(() => {
    const onChange = () => setIsFull(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', onChange);
    return () => document.removeEventListener('fullscreenchange', onChange);
  }, []);
  const toggle = useCallback(async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      /* not supported (iOS Safari): ignore */
    }
  }, []);
  const supported = typeof document.documentElement.requestFullscreen === 'function';
  return { isFull, toggle, supported };
}
