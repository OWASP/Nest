import { test, expect } from '@playwright/test'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'

test.describe('User Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockUserDetailsData },
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
    await page.goto('members/test-user')
  })
  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test User' })).toBeVisible()
    await expect(page.getByText('Test @User')).toBeVisible()
  })

  test('should have user details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'User Details' })).toBeVisible()
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
    await expect(page.getByRole('heading', { name: 'Issues' })).toBeVisible()
    await expect(page.getByText('Test Issue')).toBeVisible()
    await expect(page.getByText('test-repo-1')).toBeVisible()
  })

  test('should have user releases', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Releases' })).toBeVisible()
    await expect(page.getByText('v1.0.0')).toBeVisible()
  })

  test('should have user recent milestones', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'v2.0.0 Release' })).toBeVisible()
    await expect(page.getByText('Mar 1, 2025')).toBeVisible()
    await expect(page.getByText('Project Repo 1')).toBeVisible()
  })

  test('should have user pull requests', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Pull Requests' })).toBeVisible()
    await expect(page.getByText('Test Pull Request')).toBeVisible()
  })

  test('should have top repositories', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Repositories' })).toBeVisible()
    await expect(page.getByText('test-repo-2')).toBeVisible()
  })
})
