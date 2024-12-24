import path from 'path'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import EnvironmentPlugin from 'vite-plugin-environment'
export default defineConfig({
  plugins: [
    react(),
    EnvironmentPlugin({
      VITE_NEST_API_URL: 'http://localhost:8000/api/v1',
      VITE_NEST_ENV: 'local',
      VITE_NEST_SENTRY_DSN_URL: null,
      VITE_ALGOLIA_APP_ID: process.env.VITE_ALGOLIA_APP_ID,
      VITE_ALGOLIA_SEARCH_KEY: process.env.VITE_ALGOLIA_SEARCH_KEY,
    }),
  ],
  resolve: {
    alias: {
      '@src': path.resolve(__dirname, 'src'),
      components: path.resolve(__dirname, 'src/components'),
      utils: path.resolve(__dirname, 'src/utils'),
      lib: path.resolve(__dirname, 'src/lib'),
      pages: path.resolve(__dirname, 'src/pages'),
      '@test': path.resolve(__dirname, '__tests__/src'),
    },
  },
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
