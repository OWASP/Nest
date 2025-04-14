import { test, expect } from '@playwright/test'
import { mockOrganizationDetailsData } from '@unit/data/mockOrganizationData'

test.describe('Organization Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockOrganizationDetailsData },
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
    await page.goto('/organizations/test-org')
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Organization' })).toBeVisible()
  })

  test('should display organization details', async ({ page }) => {
    await expect(page.getByText('@test-org')).toBeVisible()
    await expect(page.getByText('San Francisco, CA')).toBeVisible()
    await expect(page.getByText('1000')).toBeVisible()
  })

  test('should display organization statistics', async ({ page }) => {
    await expect(page.getByText('5K Stars')).toBeVisible()
    await expect(page.getByText('1.2K Forks')).toBeVisible()
    await expect(page.getByText('150 Contributors')).toBeVisible()
    await expect(page.getByText('300 Issues')).toBeVisible()
    await expect(page.getByText('25 Repositories')).toBeVisible()
  })

  test('should display recent issues section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByText('Test Issue 1')).toBeVisible()
    await expect(page.getByText('Test Issue 2')).toBeVisible()
  })

  test('should display recent releases section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Release v2.0.0' }).first()).toBeVisible()
  })

  test('should display recent pull requests section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    await expect(page.getByText('Test Pull Request 1')).toBeVisible()
    await expect(page.getByText('Test Pull Request 2')).toBeVisible()
  })
})
