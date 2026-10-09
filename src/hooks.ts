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

/**
 * End-of-rest alarm. Audio contexts only start from a user gesture, so `prime()` is called
 * on the "set done" tap and `fire()` later plays the beeps.
 */
export function useAlarm() {
  const ctxRef = useRef<AudioContext | null>(null);
  const prime = useCallback(() => {
    try {
      const Ctx = window.AudioContext || (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!Ctx) return;
      if (!ctxRef.current) ctxRef.current = new Ctx();
      if (ctxRef.current.state === 'suspended') ctxRef.current.resume().catch(() => undefined);
    } catch {
      /* no audio */
    }
  }, []);
  const fire = useCallback((settings: Settings) => {
    if (settings.vibrate && 'vibrate' in navigator) {
      try {
        navigator.vibrate([400, 150, 400, 150, 900]);
      } catch {
        /* ignore */
      }
    }
    if (settings.sound && ctxRef.current) {
      try {
        const ctx = ctxRef.current;
        const t0 = ctx.currentTime;
        // Loud gym alarm: square wave near full scale, three short beeps and a long one, played twice.
        const beep = (at: number, freq: number, dur: number) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'square';
          osc.frequency.value = freq;
          gain.gain.setValueAtTime(0.0001, at);
          gain.gain.exponentialRampToValueAtTime(0.95, at + 0.015);
          gain.gain.setValueAtTime(0.95, at + dur - 0.04);
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
