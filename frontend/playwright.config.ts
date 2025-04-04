import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  fullyParallel: true,
  projects: [
    {
      name: 'Chromium',
      use: { browserName: 'chromium' },
    },
    {
      name: 'Mobile Safari - iPhone 13',
      use: {
        ...devices['iPhone 13'],
      },
    },
  ],
  reporter: [['list', { printSteps: true }]],
  retries: 2,
  testDir: './__tests__/e2e',
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    trace: 'off',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
  },
})
