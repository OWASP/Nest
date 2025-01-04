import path from 'path'

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
      VITE_ALGOLIA_SEARCH_API_KEY: process.env.VITE_ALGOLIA_SEARCH_API_KEY,
      VITE_API_URL: process.env.VITE_API_URL,
      VITE_ENVIRONMENT: process.env.VITE_ENVIRONMENT,
      VITE_SENTRY_DSN: process.env.VITE_SENTRY_DSN,
    }),
  ],
  resolve: {
    alias: {
      components: path.resolve(__dirname, 'src/components'),
      lib: path.resolve(__dirname, 'src/lib'),
      pages: path.resolve(__dirname, 'src/pages'),
      utils: path.resolve(__dirname, 'src/utils'),
      'sentry.config': path.resolve(__dirname, 'src/sentry.config.ts'),
      '@tests': path.resolve(__dirname, '__tests__'),
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
