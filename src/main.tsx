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
  // The offline service worker is only for the browser / PWA; the Android app ships its files inside the APK.
  if (!isNative) registerSW({ immediate: true });
  createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}

boot();
