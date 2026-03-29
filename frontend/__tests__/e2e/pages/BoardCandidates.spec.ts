import { test, expect } from '@playwright/test'

test.describe('Board Candidates Page', () => {
  const validYear = '2024'
  const invalidYear = '1800'
  const validUrl = `/board/${validYear}/candidates`
  const invalidUrl = `/board/${invalidYear}/candidates`

  test('should render the page without crashing', async ({ page }) => {
    const response = await page.goto(validUrl, { timeout: 25000 })
    expect(response).not.toBeNull()
    expect(response!.status()).toBe(200)
  })

  test('should show board not found for invalid year', async ({ page }) => {
    await page.goto(invalidUrl, { timeout: 25000, waitUntil: 'domcontentloaded' })
    await expect(page.getByText('Board not found')).toBeVisible()
  })

  test('should show correct error message for invalid year', async ({ page }) => {
    await page.goto(invalidUrl, { timeout: 25000, waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: '404' })).toBeVisible()
    await expect(
      page.getByText(`Sorry, the board information for ${invalidYear} doesn't exist`)
    ).toBeVisible()
  })

  test('should have navigation bar', async ({ page }) => {
    await page.goto(validUrl, { timeout: 25000, waitUntil: 'domcontentloaded' })
    await expect(page.locator('#navbar-sticky')).toBeVisible()
  })
})