import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // required to accept connections inside Docker
    port: 3000,
    proxy: {
      // Requests to /api/* are forwarded to the FastAPI backend.
      // "backend" resolves to the backend container via Docker's internal DNS.
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})
