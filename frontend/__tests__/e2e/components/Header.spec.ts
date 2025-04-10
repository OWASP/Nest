import { mockHomeData } from '@e2e/data/mockHomeData'
import { test, expect, devices } from '@playwright/test'

// Desktop tests
test.describe('Header - Desktop (Chrome)', () => {
  test.use({
    viewport: { width: 1280, height: 800 },
    isMobile: false,
  })

  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: mockHomeData,
      })
    })
    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])
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

  test('should have nav links including community dropdown', async ({ page }) => {
    const navbar = page.locator('#navbar-sticky')

    // Check main nav links
    await expect(navbar.getByRole('link', { name: 'About' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Contribute' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Projects' })).toBeVisible()
    await expect(navbar.getByText('Community')).toBeVisible()

    const communityLink = navbar.getByText('Community')
    await communityLink.hover()

    // Assert dropdown options appear
    await expect(navbar.getByRole('link', { name: 'Chapters' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Snapshots' })).toBeVisible()
    await expect(navbar.getByRole('link', { name: 'Users' })).toBeVisible()
  })
})

// Mobile tests (iPhone 13)
test.use({
  ...devices['iPhone 13'],
  isMobile: true,
})

test.describe('Header - Mobile (iPhone 13)', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: mockHomeData,
      })
    })
    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])
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

    await expect(page.getByRole('banner').getByText('Community', { exact: true })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Chapters' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Snapshots' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Users' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Projects' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Contribute' })).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'About' })).toBeVisible()
  })
})
