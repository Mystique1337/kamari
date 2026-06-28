import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'icons/kamari.svg'],
      manifest: {
        name: 'Kámárí — Age Verification',
        short_name: 'Kámárí',
        description: 'African-focused, privacy-first age verification.',
        theme_color: '#213A6B',
        background_color: '#14213D',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'icons/kamari.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
          { src: 'icons/kamari-maskable.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'maskable' },
        ],
      },
    }),
  ],
  server: { port: 5173 },
});
