import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import os from 'os'

const platform = os.platform()
console.log("platofrom" , platform)
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: platform === 'win32' || platform === 'linux',
      interval: 1000,
    },
    host: true,
    strictPort: true,
    port: 3000,
  },
})
