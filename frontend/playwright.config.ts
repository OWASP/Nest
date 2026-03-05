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
    baseURL: 'http://localhost:3001',
  },
  webServer: {
    command: 'pnpm run build && cross-env NEXT_SERVER_DISABLE_SSR=true pnpm run start -p 3001',
    timeout: 300_000,
    url: 'http://localhost:3001',
    reuseExistingServer: false,
  },
  workers: process.env.CI ? 1 : 2,
})
