import { defineConfig } from '@playwright/test'

export default defineConfig({
  fullyParallel: true,
  projects: [
    {
      name: 'Chromium',
      use: { browserName: 'chromium' },
    },
  ],
  reporter: [['list', { printSteps: true }]],
  testDir: './__tests__/e2e',
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    trace: 'off',
  },
  webServer: {
    command: 'npm run build && npm run start',
    url: 'http://localhost:3000',
  },
})
