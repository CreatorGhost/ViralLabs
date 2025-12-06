import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      // Proxy API requests to backend during development
      '/auth': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/generate': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/regenerate': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/thumbnail': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/thumbnails': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/upload': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/face': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/session': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/search': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/audio': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/image': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
  },
});

