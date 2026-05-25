import { test, expect } from '@playwright/test'

test.describe('Board Candidates Page', () => {
  const validYear = '2025'
  const invalidYear = '2020'
  const validUrl = `/board/${validYear}/candidates`
  const invalidUrl = `/board/${invalidYear}/candidates`

  test('should load board candidates page with heading and navigation', async ({ page }) => {
    const response = await page.goto(validUrl)
    expect(response).not.toBeNull()
    expect(response!.status()).toBe(200)
    await expect(
      page.getByRole('heading', { name: `${validYear} Board of Directors Candidates` })
    ).toBeVisible()
    await expect(page.locator('#navbar-sticky')).toBeVisible()
  })

  test('should show 404 and board not found for invalid year', async ({ page }) => {
    await page.goto(invalidUrl)
    await expect(page.getByRole('heading', { level: 1, name: '404' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Board not found' })).toBeVisible()
    await expect(
      page.getByText(`Sorry, the board information for ${invalidYear} doesn't exist`)
    ).toBeVisible()
  })
})
