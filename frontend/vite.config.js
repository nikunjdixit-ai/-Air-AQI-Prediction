import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    emptyOutDir: false,
  },
  server: {
    proxy: {
      '/health': 'http://127.0.0.1:5000',
      '/status': 'http://127.0.0.1:5000',
      '/live': 'http://127.0.0.1:5000',
      '/predict': 'http://127.0.0.1:5000',
      '/historical': 'http://127.0.0.1:5000',
      '/weather': 'http://127.0.0.1:5000',
      '/health-risk': 'http://127.0.0.1:5000',
      '/agent': 'http://127.0.0.1:5000',
    },
  },
})
