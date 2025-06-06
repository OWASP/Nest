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
   test('should display the frontend version', async ({ page }) => {
    // The version is read from the environment at build time,
    // so we just check for its presence in the rendered footer.
    // This regex looks for "Frontend Version: " followed by a version number like "x.y.z".
    const versionRegex = /Frontend Version: \d+\.\d+\.\d+/;
    await expect(page.getByText(versionRegex)).toBeVisible();
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
  test('should display the frontend version', async ({ page }) => {
    // The version is read from the environment at build time,
    // so we just check for its presence in the rendered footer.
    // This regex looks for "Frontend Version: " followed by a version number like "x.y.z".
    const versionRegex = /Frontend Version: \d+\.\d+\.\d+/;
    await expect(page.getByText(versionRegex)).toBeVisible();
  })
})
