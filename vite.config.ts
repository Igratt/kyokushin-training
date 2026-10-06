import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

// Deployed at https://igratt.github.io/kyokushin/ — the base and the manifest URLs are absolute on purpose:
// Android's WebAPK installer is picky about relative start_url/scope. For another host change BASE (e.g. '/').
const BASE = '/kyokushin-training/';

export default defineConfig({
  base: BASE,
  build: { assetsDir: 'static' },
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['assets/*.webp'],
      includeManifestIcons: false,
      // Kept deliberately identical in shape to the Trenkės manifest, which installs fine on the same phone:
      // relative start_url/scope, icons at the root, no orientation/id. Icons are NOT precached so the
      // browser and Google's WebAPK server always see the same bytes. Hosted at a fresh path because the
      // first Android install at /kyokushin/ got stuck and every retry there failed.
      manifest: {
        name: 'Kyokushin Training',
        short_name: 'Kyokushin',
        lang: 'lt',
        description: '3 dienų Kyokushin sporto salės programa su treniruotės vedliu.',
        start_url: './',
        scope: './',
        display: 'standalone',
        background_color: '#0B1020',
        theme_color: '#0B1020',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,webp,svg,ico}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts',
              expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 365 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
    }),
  ],
});
