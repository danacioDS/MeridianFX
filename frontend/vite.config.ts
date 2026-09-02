import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    strictPort: true, // Si el puerto está ocupado, falla en lugar de cambiar
  },
  build: {
    minify: false,
    target: 'es2020',
    chunkSizeWarningLimit: 1000,
  },
})
