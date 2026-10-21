import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// base './' da sajt radi i u podfolderu (GitHub Pages: /Nemi/kern/)
export default defineConfig({
  base: './',
  plugins: [react()],
  build: { target: 'es2020', chunkSizeWarningLimit: 1200 },
});
