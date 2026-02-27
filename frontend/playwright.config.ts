import os from 'node:os'
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  expect: {
    timeout: 30000,
  },
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
    },
  ],
  reporter: [['list', { printSteps: true }]],
  retries: 2,
  testDir: './__tests__/e2e',
  timeout: 120_000,
  use: {
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    headless: true,
    trace: 'off',
  },
  workers: os.cpus().length,
})
