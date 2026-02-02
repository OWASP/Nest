import { test, expect, devices, Page, BrowserContext } from '@playwright/test'

// Desktop tests
test.describe.serial('Footer - Desktop (Chrome)', () => {
  let page: Page
  let context: BrowserContext

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext({
      ...devices['Desktop Chrome'],
    })
    page = await context.newPage()
    await page.goto('/', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have buttons', async () => {
    await expect(page.getByRole('button', { name: 'OWASP Nest' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Resources' })).toBeVisible()
  })
  test('should have links', async () => {
    await expect(page.getByRole('link', { name: 'OWASP Nest Bluesky' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest GitHub' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest LinkedIn' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest Slack' })).toBeVisible()
  })
})

test.describe.serial('Footer - Mobile (iPhone 13)', () => {
  let page: Page
  let context: BrowserContext

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext({
      ...devices['iPhone 13'],
    })
    page = await context.newPage()
    await page.goto('/')
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have buttons', async () => {
    await expect(page.getByRole('button', { name: 'OWASP Nest' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Resources' })).toBeVisible()
  })

  test('should show sub-menu when menu clicked', async () => {
    await page.getByRole('button', { name: 'OWASP Nest' }).click()
    // only check if the sub-menu is visible
    await expect(page.getByRole('link', { name: 'GSoC 2026' })).toBeVisible()
  })
  test('should have links', async () => {
    await expect(page.getByRole('link', { name: 'OWASP Nest Bluesky' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest GitHub' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'OWASP Nest Slack' })).toBeVisible()
  })
})
