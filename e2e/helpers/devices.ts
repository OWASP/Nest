import { devices } from '@playwright/test'

// iPhone 13 profile without WebKit; use Chromium for mobile emulation in CI and locally.
const { defaultBrowserType: _webkit, ...iphone13 } = devices['iPhone 13']

export const iphone13Chromium = {
  ...iphone13,
  browserName: 'chromium' as const,
}
