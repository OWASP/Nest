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
    await page.goto('/organization/test-org')
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Organization' })).toBeVisible()
    await expect(
      page.getByText('This is a test organization with a detailed description')
    ).toBeVisible()
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
    await expect(page.getByText('Release v1.0.0')).toBeVisible()
    await expect(page.getByText('Release v2.0.0')).toBeVisible()
  })

  test('should display top contributors section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(page.getByText('User One')).toBeVisible()
    await expect(page.getByText('User Two')).toBeVisible()
    await expect(page.getByText('User Three')).toBeVisible()
  })

  test('should navigate to repository details when clicking on a repository', async ({ page }) => {
    await page.getByRole('button', { name: 'test-repo-1' }).click()
    expect(page.url()).toContain('repositories')
  })
})
