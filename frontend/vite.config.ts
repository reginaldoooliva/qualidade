import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 5173,
    watch: {
      // Bind mounts do Windows -> container Linux (Docker Desktop) não emitem eventos
      // inotify, então o watcher precisa fazer polling para detectar mudanças de arquivo.
      usePolling: true,
      interval: 300,
    },
  },
})
