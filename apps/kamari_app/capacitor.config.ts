import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.kamari.app',
  appName: 'Kamari',
  webDir: 'dist',
  server: { androidScheme: 'https' },
  plugins: {
    Camera: {
      // Front camera, no gallery - this is a live selfie age check.
    },
  },
};

export default config;
