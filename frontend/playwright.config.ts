import os from 'os'
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  fullyParallel: true,
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
    {
      name: 'Mobile Safari - iPhone 13',
      use: {
        ...devices['iPhone 13'],
      },
      expect: {
        timeout: 10000, // Mobile Safari needs more time to render
      },
    },
  ],
  reporter: [['list', { printSteps: true }]],
  retries: 2,
  testDir: './__tests__/e2e',
  timeout: 120_000,
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    trace: 'off',
  },
  webServer: {
    command: 'pnpm run build && NEXT_SERVER_DISABLE_SSR=true pnpm run start',
    timeout: 300_000,
    url: 'http://localhost:3000',
  },
  workers: os.cpus().length,
})
