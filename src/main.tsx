import React from 'react';
import { createRoot } from 'react-dom/client';
import { registerSW } from 'virtual:pwa-register';
import App from './App';
import { hydrateStorage, isNative } from './native';
import { STORAGE_KEYS } from './storage';
import './styles.css';

async function boot() {
  // Android app: pull saved data out of the app's own storage before the first render.
  await hydrateStorage(STORAGE_KEYS);
  // The offline service worker runs in the browser and in the Android app (which loads the live site and
  // caches it through the same worker, so updates arrive on the next launch); not for files bundled in an APK.
  if (!(isNative && location.hostname === 'localhost')) registerSW({ immediate: true });
  createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}

boot();
