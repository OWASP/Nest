import { test, expect } from '@playwright/test'

test.describe('Community Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/community', { timeout: 25000 })
  })

  test('renders main heading and description', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Community' })).toBeVisible()
    await expect(page.getByText('Explore the vibrant OWASP community')).toBeVisible()
  })

  test('renders explore resources section', async ({ page }) => {
    await expect(page.getByText('Explore Resources')).toBeVisible()
  })

  test('renders ways to engage section', async ({ page }) => {
    await expect(page.getByText('Ways to Engage')).toBeVisible()
  })

  test('renders call to action section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Ready to Get Involved?' })).toBeVisible()
  })

  test('renders join slack link', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Join Slack' })).toBeVisible()
  })

  test('renders navigation links to community sections', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Chapters' }).first()).toBeVisible()
    await expect(page.getByRole('link', { name: 'Members' }).first()).toBeVisible()
    await expect(page.getByRole('link', { name: 'Organizations' }).first()).toBeVisible()
  })

  test('has no console errors', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })
    await page.goto('/community', { timeout: 25000 })
    expect(errors).toHaveLength(0)
  })
})

test.describe('Community Snapshots Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/community/snapshots', { timeout: 25000 })
  })

  test('renders snapshots page without crashing', async ({ page }) => {
    await expect(page.locator('body')).toBeVisible()
  })
})
