import { defineConfig } from '@playwright/test'

export default defineConfig({
  fullyParallel: true,
  projects: [
    {
      name: 'Chromium',
      use: { browserName: 'chromium' },
    },
    // {
    //   name: 'Mobile Safari - iPhone 13',
    //   use: {
    //     ...devices['iPhone 13'],
    //   },
    // },
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
    command: 'pnpm run build && pnpm run start',
    timeout: 120_000,
    url: 'http://localhost:3000',
  },
})
