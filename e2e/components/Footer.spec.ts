import { iphone13Chromium } from '@e2e/helpers/devices'
import { test, expect } from '@playwright/test'

// Desktop tests
test.describe('Footer - Desktop (Chrome)', () => {
  test.use({
    viewport: { width: 1280, height: 800 },
    isMobile: false,
  })

  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
  })

  test('should have buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'OWASP Nest' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Resources' })).toBeVisible()
  })

  test('should have links', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'OWASP Nest on Bluesky' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest on GitHub' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest on LinkedIn' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest on Slack' })).toBeVisible()
  })

  test('should show tooltip on social link hover', async ({ page }) => {
    await page.getByRole('link', { name: 'OWASP Nest on GitHub' }).hover()
    await expect(page.getByRole('tooltip')).toHaveText('OWASP Nest on GitHub')
  })
})

// Mobile tests (iPhone 13, Chromium)
test.use({
  ...iphone13Chromium,
  isMobile: true,
})

test.describe('Footer - Mobile (iPhone 13)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
  })

  test('should have buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'OWASP Nest' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Resources' })).toBeVisible()
  })

  test('should show sub-menu when menu clicked', async ({ page }) => {
    await page.getByRole('button', { name: 'OWASP Nest' }).click()
    // only check if the sub-menu is visible
    await expect(page.getByRole('link', { name: 'GSoC 2026' })).toBeVisible()
  })

  test('should have links', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'OWASP Nest on Bluesky' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest on GitHub' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest on Slack' })).toBeVisible()
  })
})
