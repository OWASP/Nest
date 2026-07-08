import { iphone13Chromium } from '@e2e/helpers/devices'
import { test, expect } from '@playwright/test'

// Desktop tests
test.describe('Header - Desktop (Chrome)', () => {
  test.use({
    viewport: { width: 1280, height: 800 },
    isMobile: false,
  })

  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
  })

  test('should have logo', async ({ page }) => {
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'OWASP Logo Nest' })
    ).toBeVisible()
  })

  test('should have buttons', async ({ page }) => {
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'Star', exact: true })
    ).toBeVisible()
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'Sponsor' })
    ).toBeVisible()
  })

  test('should have nav links including Community', async ({ page }) => {
    const navbar = page.locator('#navbar-sticky')

    await expect(navbar.getByRole('link', { name: 'Community' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Projects' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Contribute' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'About' })).toBeVisible()
  })
})

// Mobile tests (iPhone 13, Chromium)
test.use({
  ...iphone13Chromium,
  isMobile: true,
})

test.describe('Header - Mobile (iPhone 13)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
  })

  test('should have logo', async ({ page }) => {
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'OWASP Logo Nest' })
    ).toBeVisible()
  })

  test('should have mobile menu button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /menu/i })).toBeVisible()
  })

  test('should show button when menu clicked', async ({ page }) => {
    const menuButton = page.getByRole('button', { name: /menu/i })
    await menuButton.click()
    await expect(page.getByRole('link', { name: 'Star On Github' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Sponsor Us' })).toBeVisible()
  })

  test('should show navigation when menu clicked', async ({ page }) => {
    const menuButton = page.getByRole('button', { name: /menu/i })
    await menuButton.click()

    await expect(page.getByRole('banner').getByRole('link', { name: 'Community' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Projects' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Contribute' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'About' })).toBeVisible()
  })
})
