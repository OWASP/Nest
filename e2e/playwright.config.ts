import { iphone13Chromium } from '@e2e/helpers/devices'
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
      name: 'Mobile Chrome - iPhone 13',
      use: iphone13Chromium,
    },
  ],
  reporter: process.env.CI
    ? [
        ['list', { printSteps: true }],
        ['github'],
      ]
    : [['list', { printSteps: true }]],
  retries: 2,
  testDir: '.',
  timeout: 120_000,
  use: {
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    headless: true,
    trace: 'off',
  },
  workers: process.env.CI ? 2 : os.cpus().length,
})
