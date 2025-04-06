import { defineConfig } from '@playwright/test'

export default defineConfig({
  timeout: 45000,
  fullyParallel: true,
  retries: 1,
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
    timeout: 120 * 1000,
    command: 'pnpm run build && pnpm run start',
    url: 'http://localhost:3000',
  },
})
