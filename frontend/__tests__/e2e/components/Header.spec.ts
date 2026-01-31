import { test, expect, devices, BrowserContext, Page } from '@playwright/test'

// Desktop tests
test.describe.serial('Header - Desktop (Chrome)', () => {
  let context: BrowserContext
  let page: Page

  test.use({
    viewport: { width: 1280, height: 800 },
    isMobile: false,
  })

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have logo', async () => {
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'OWASP Logo Nest' })
    ).toBeVisible()
  })

  test('should have buttons', async () => {
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'Star', exact: true })
    ).toBeVisible()
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'Sponsor' })
    ).toBeVisible()
  })

  test('should have nav links including community dropdown', async () => {
    const navbar = page.locator('#navbar-sticky')

    // Check main nav links
    await expect(navbar.getByRole('link', { name: 'About' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Contribute' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Projects' })).toBeVisible()
    await expect(navbar.getByRole('button', { name: 'Community' })).toBeVisible()

    const communityButton = navbar.getByRole('button', { name: 'Community' })
    await communityButton.click()

    await expect(navbar.getByRole('link', { name: 'Chapters' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Members' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Organizations' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Snapshots' })).toBeVisible()
  })

  test('all dropdown triggers should use pointer cursor', async () => {
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

test.describe.serial('Header - Mobile (iPhone 13)', () => {
  let page: Page
  let context: BrowserContext

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have logo', async () => {
    await expect(
      page.locator('#navbar-sticky').getByRole('link', { name: 'OWASP Logo Nest' })
    ).toBeVisible()
  })

  test('should have mobile menu button', async () => {
    await expect(page.getByRole('button', { name: /menu/i })).toBeVisible()
  })
  test('should show button when menu clicked', async () => {
    const menuButton = page.getByRole('button', { name: /menu/i })
    await menuButton.click()
    await expect(page.getByRole('link', { name: 'Star On Github' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Sponsor Us' })).toBeVisible()
  })
  test('should show navigation when menu clicked', async () => {
    const menuButton = page.getByRole('button', { name: /menu/i })
    await menuButton.click()

    await expect(page.getByRole('banner').getByRole('link', { name: 'Chapters' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Members' })).toBeVisible()
    await expect(
      page.getByRole('banner').getByRole('link', { name: 'Organizations' })
    ).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Snapshots' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Projects' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Contribute' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'About' })).toBeVisible()
  })
})
