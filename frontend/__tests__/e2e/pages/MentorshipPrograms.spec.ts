import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockPrograms } from '@mockData/mockProgramData'
import { test, expect } from '@playwright/test'

test.describe('Mentorship Programs Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: mockPrograms, nbPages: 1 }),
      })
    })
    await page.goto('/mentorship/programs', { timeout: 25000 })
  })

  test('renders program card from mock data', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Program 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Program 1.')).toBeVisible()
  })

  test('search input is visible', async ({ page }) => {
    await expect(page.getByPlaceholder('Search for programs...')).toBeVisible()
  })

  test('displays "No programs found" when there are no programs', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/mentorship/programs', { timeout: 25000 })
    await expect(page.getByText('No programs found')).toBeVisible()
  })

  test('breadcrumb renders correct segments on /mentorship/programs', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Mentorship'])
  })
})
