import React from 'react';
import { createRoot } from 'react-dom/client';
import { registerSW } from 'virtual:pwa-register';
import App from './App';
import { isNative } from './native';
import { hydrate } from './storage';
import './styles.css';

async function boot() {
  // Android app: merge the app's own storage into the WebView copy before the first render.
  await hydrate();
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
