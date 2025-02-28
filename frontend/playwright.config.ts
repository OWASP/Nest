import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  fullyParallel: true,
  reporter: [['list', { printSteps: true }]],
  testDir: './__tests__/e2e',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'off',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
  },
})
