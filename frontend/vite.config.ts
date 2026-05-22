import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/role-assets': 'http://localhost:8000',
      '/role-versions': 'http://localhost:8000',
      '/test-runs': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})