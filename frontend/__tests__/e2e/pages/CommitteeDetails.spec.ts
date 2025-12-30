import { test, expect } from '@playwright/test'

test.describe('Committee Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/committees/events', { timeout: 120000 })
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Committee' })).toBeVisible()
    await expect(page.getByText('This is a test committee')).toBeVisible()
  })

  test('should have committee details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Committee Details' })).toBeVisible()
    await expect(page.getByText('Last Updated: Dec 13, 2024')).toBeVisible()
    await expect(page.getByText('Leaders: Leader 1, Leader 2')).toBeVisible()
    await expect(page.getByRole('link', { name: 'https://owasp.org/test-committee' })).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 1' })).toBeVisible()
    await expect(page.getByText('Contributor 1')).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 2' })).toBeVisible()
    await expect(page.getByText('Contributor 2')).toBeVisible()
  })
})
