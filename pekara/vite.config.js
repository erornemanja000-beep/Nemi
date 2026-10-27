// Krume: Vite (vanilla JS). Relativne putanje, da dist radi i iz podfoldera na Netlify-ju.
// Dev server sluša samo na localhost (bez --host).
import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    assetsInlineLimit: 0, // fontovi i slike ostaju fajlovi (keš, preload)
  },
});
