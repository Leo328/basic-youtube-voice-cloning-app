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
      'backend-basic-youtube-voice-cloning-app.onrender.com',
      '.onrender.com'  // Allow all subdomains on render.com
    ]
  },
  server: {
    port: process.env.PORT || 5173,
    host: '0.0.0.0'
  },
  define: {
    // Production URL for the backend API (no 'backend-' prefix)
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(process.env.VITE_API_BASE_URL || 'https://backend-basic-youtube-voice-cloning-app.onrender.com')
  }
})
