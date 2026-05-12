import { test, expect, devices } from '@playwright/test'

// Desktop tests
test.describe('Header - Desktop (Chrome)', () => {
  test.use({
    viewport: { width: 1280, height: 800 },
    isMobile: false,
  })

  test.beforeEach(async ({ page }) => {
    await page.goto('/')
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

  test('all dropdown triggers should use pointer cursor', async ({ page }) => {
    await page.goto('/')

    const dropdownButtons = page.locator('#navbar-sticky button')

    const count = await dropdownButtons.count()
    expect(count).toBeGreaterThan(0)

    for (let i = 0; i < count; i++) {
      const btn = dropdownButtons.nth(i)
      const cursor = await btn.evaluate((el) => globalThis.getComputedStyle(el).cursor)
      expect(cursor).toBe('pointer')
    }
  })
})

// Mobile tests (iPhone 13)
test.use({
  ...devices['iPhone 13'],
  isMobile: true,
})

test.describe('Header - Mobile (iPhone 13)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
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
