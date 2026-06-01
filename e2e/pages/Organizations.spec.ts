import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockOrganizationData } from '@mockData/mockOrganizationData'
import { test, expect } from '@playwright/test'

test.describe('Organization Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockOrganizationData.hits,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/organizations', { timeout: 25000 })
  })

  test('renders organization data correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Organization' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Another Organization' })).toBeVisible()

    const viewDetailsButtons = page.getByRole('button', { name: 'View Profile' })
    await expect(viewDetailsButtons).toHaveCount(2)
  })

  test('displays followers and repositories counts correctly', async ({ page }) => {
    await expect(page.getByText('1k')).toBeVisible()
    await expect(page.getByText('1.5k')).toBeVisible()
  })

  test('breadcrumb renders correct segments on /organizations', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Organizations'])
  })

  test('navigation to organization details works', async ({ page }) => {
    await page.getByRole('button', { name: 'View Profile' }).first().click()
    await expect(page).toHaveURL(/\/organizations\/[^/]+/)
  })
})
