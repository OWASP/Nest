import { test, expect } from '@playwright/test'

test.describe('Board Candidates Page', () => {
  test('should render the page without crashing', async ({ page }) => {
    const response = await page.goto('/board/2024/candidates', { timeout: 25000 })
    expect(response?.status()).not.toBe(500)
  })

  test('should show board not found for invalid year', async ({ page }) => {
    await page.goto('/board/1800/candidates', { timeout: 25000, waitUntil: 'domcontentloaded' })
    await expect(page.getByText('Board not found')).toBeVisible()
  })

  test('should show correct error message for invalid year', async ({ page }) => {
    await page.goto('/board/1800/candidates', { timeout: 25000, waitUntil: 'domcontentloaded' })
    await expect(
      page.getByText("Sorry, the board information for 1800 doesn't exist")
    ).toBeVisible()
  })

  test('should have navigation bar', async ({ page }) => {
    await page.goto('/board/2024/candidates', { timeout: 25000, waitUntil: 'domcontentloaded' })
    await expect(page.locator('#navbar-sticky')).toBeVisible()
  })
})