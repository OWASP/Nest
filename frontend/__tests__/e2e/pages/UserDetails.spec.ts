import { test, expect } from '@playwright/test'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'
test.describe('UserDetails Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockUserDetailsData },
      })
    })
    await page.goto('community/users/test-user')
  })
  test('should have a user name and avatar', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test User' })).toBeVisible()
    await expect(page.getByRole('link', { name: '@testuser' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Test User' })).toBeVisible()
  })

  test('should have user details', async ({ page }) => {
    await expect(page.getByText('Test Company')).toBeVisible()
    await expect(page.getByText('Test Location')).toBeVisible()
    await expect(page.getByRole('link', { name: 'testuser@example.com' })).toBeVisible()
  })

  test('should have recent issues', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Test Issue' })).toBeVisible()
    await expect(page.getByText('8/7/2024').first()).toBeVisible()
  })

  test('should have recent releases', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'v1.0.0' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'testuser/test-repo' }).nth(1)).toBeVisible()
    await expect(page.getByText('8/7/2024').first()).toBeVisible()
  })
})
