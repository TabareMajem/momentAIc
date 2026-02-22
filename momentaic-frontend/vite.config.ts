import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: 2685,
      host: '0.0.0.0',
      allowedHosts: ['momentaic.com', 'www.momentaic.com', 'api.momentaic.com', 'localhost', '127.0.0.1'],
    },
    preview: {
      port: 2685,
      host: '0.0.0.0',
      allowedHosts: true,
    },
    plugins: [react()],
    // Security: No API keys are injected into frontend builds
    // All AI calls must go through the backend API
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      minify: 'esbuild',
    }
  };
});
