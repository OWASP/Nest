import { mockHomeData } from '@e2e/data/mockHomeData'
import { test, expect, devices } from '@playwright/test'

// Desktop tests
test.describe('Footer - Desktop (Chrome)', () => {
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
  test('should have buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'OWASP Nest' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Resources' })).toBeVisible()
  })
  test('should have links', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'OWASP Nest Bluesky' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest GitHub' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest LinkedIn' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest Slack' })).toBeVisible()
  })

  test('should display version when available', async ({ page }) => {
    const versionElement = page.locator('text=Release Version:')
    if (await versionElement.isVisible()) {
      await expect(versionElement).toBeVisible()
      await expect(page.locator('.font-mono')).toBeVisible()
    }
  })
})

// Mobile tests (iPhone 13)
test.use({
  ...devices['iPhone 13'],
  isMobile: true,
})

test.describe('Footer - Mobile (iPhone 13)', () => {
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
  test('should have buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'OWASP Nest' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Resources' })).toBeVisible()
  })

  test('should show sub-menu when menu clicked', async ({ page }) => {
    await page.getByRole('button', { name: 'OWASP Nest' }).click()
    // only check if the sub-menu is visible
    await expect(page.getByRole('link', { name: 'GSoC 2025' })).toBeVisible()
  })
  test('should have links', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'OWASP Nest Bluesky' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest GitHub' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest Slack' })).toBeVisible()
  })

  test('should display version when available', async ({ page }) => {
    // Check if version is displayed when NEXT_PUBLIC_RELEASE_VERSION is set
    const versionElement = page.locator('text=Release Version:')
    if (await versionElement.isVisible()) {
      await expect(versionElement).toBeVisible()
      await expect(page.locator('.font-mono')).toBeVisible()
    }
  })
})
