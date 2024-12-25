import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import EnvironmentPlugin from 'vite-plugin-environment'

export default defineConfig({
  build: {
    sourcemap: true,
  },
  plugins: [
    react(),
    EnvironmentPlugin({
      VITE_ALGOLIA_APP_ID: process.env.VITE_ALGOLIA_APP_ID,
      VITE_ALGOLIA_SEARCH_KEY: process.env.VITE_ALGOLIA_SEARCH_KEY,
      VITE_NEST_API_URL: process.env.VITE_NEST_API_URL,
      VITE_NEST_ENV: process.env.VITE_NEST_ENV,
      VITE_NEST_SENTRY_DSN_URL: process.env.VITE_SENTRY_DSN_URL,
    }),
  ],
  server: {
    watch: {
      usePolling: true,
      interval: 1000,
    },
    host: true,
    strictPort: true,
    port: 3000,
  },
})
