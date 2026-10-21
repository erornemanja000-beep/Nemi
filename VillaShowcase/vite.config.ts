import { defineConfig } from 'vite'

// Relative base so the built site works from any folder or sub-path
// (GitHub Pages, Netlify, a USB stick, a laptop without internet).
export default defineConfig({
  base: './',
})
