import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// A relative base works both at a domain root (Cloudflare Pages) and under a
// project path (GitHub Pages: https://<user>.github.io/<repo>/).
// Set DANDAN_BASE=/<repo>/ for an absolute base instead.
export default defineConfig({
  base: process.env.DANDAN_BASE ?? './',
  plugins: [vue()],
  build: {
    target: 'es2022',
    // The font files are served from public/ as they are; never inline them.
    assetsInlineLimit: 0,
  },
})
