import { test, expect, Page } from '@playwright/test'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'

function getFirstHeading(page: Page, name: string) {
  return page.getByRole('heading', { name }).first()
}

test.describe('User Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockUserDetailsData },
      })
    })
    await page.goto('community/users/test-user')
  })
  test('should have a heading and summary', async ({ page }) => {
    await expect(getFirstHeading(page, 'Test User')).toBeVisible()
    await expect(page.getByText('Test @User')).toBeVisible()
  })

  test('should have user details block', async ({ page }) => {
    await expect(getFirstHeading(page, 'User Details')).toBeVisible()
    await expect(page.getByText('Location: Test Location')).toBeVisible()
    await expect(page.getByText('Email: testuser@example.com')).toBeVisible()
    await expect(page.getByText('Company: Test Company')).toBeVisible()
  })

  test('should have user stats block', async ({ page }) => {
    await expect(page.getByText('10 Followers')).toBeVisible()
    await expect(page.getByText('5 Following')).toBeVisible()
    await expect(page.getByText('3 Repositories')).toBeVisible()
  })

  test('should have user issues', async ({ page }) => {
    await expect(getFirstHeading(page, 'Issues')).toBeVisible()
    await expect(page.getByText('Test Issue')).toBeVisible()
    await expect(page.getByText('5 Comments')).toBeVisible()
  })

  test('should have user releases', async ({ page }) => {
    await expect(getFirstHeading(page, 'Releases')).toBeVisible()
    await expect(page.getByText('v1.0.0')).toBeVisible()
  })

  test('should have user pull requests', async ({ page }) => {
    await expect(getFirstHeading(page, 'Pull Requests')).toBeVisible()
    await expect(page.getByText('Test Pull Request')).toBeVisible()
  })

  test('should have top repositories', async ({ page }) => {
    await expect(getFirstHeading(page, 'Repositories')).toBeVisible()
    await expect(page.getByText('Test Repo')).toBeVisible()
  })
})
