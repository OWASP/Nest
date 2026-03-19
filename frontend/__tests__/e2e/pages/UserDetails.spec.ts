import { test, expect } from '@playwright/test'

test.describe('User Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/members/arkid15r', { timeout: 25000 })
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Arkadii Yakovets', exact: true })).toBeVisible()
    await expect(page.getByText('@arkid15r')).toBeVisible()
  })

  test('should have user details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'User Details' })).toBeVisible()
    await expect(page.getByText(/Location:/i)).toBeVisible()
    await expect(page.getByText(/Email:/i)).toBeVisible()
  })

  test('should have user stats block', async ({ page }) => {
    const stats = ['Followers', 'Following', 'Repositories']
    for (const stat of stats) {
      const text = String.raw`\d.*${stat}`
      await expect(
        page
          .locator('div')
          .filter({ hasText: new RegExp(text) })
          .first()
      ).toBeVisible()
    }
  })

  test('should have user activity sections', async ({ page }) => {
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Issues' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Pull Requests' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Repositories' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Milestones' })
    ).toBeVisible()
    const firstRepo = page.locator('div').filter({ hasText: 'Repositories' }).locator('a').first()
    await expect(firstRepo).toBeVisible()
  })
})
