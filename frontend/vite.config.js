import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  preview: {
    port: process.env.PORT || 5173,
    host: '0.0.0.0',
    allowedHosts: [
      'frontend-basic-youtube-voice-cloning-app.onrender.com',
      '.onrender.com'  // Allow all subdomains on render.com
    ]
  },
  server: {
    port: process.env.PORT || 5173,
    host: '0.0.0.0'
  }
})
