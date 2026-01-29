import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockCommitteeData } from '@mockData/mockCommitteeData'
import { test, expect } from '@playwright/test'

test.describe('Committees Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockCommitteeData.committees,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/committees', { timeout: 25000 })
  })

  test('renders committee data correctly', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Committee 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Committee 1')).toBeVisible()
    await expect(page.getByRole('link', { name: "Sam Stepanyan's avatar" })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Learn more about Committee' })).toBeVisible()
  })

  test('displays "No committees found" when there are no committees', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/committees')
    await expect(page.getByText('No committees found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = await page.getByRole('button', { name: '2' })
    await nextPageButton.waitFor({ state: 'visible' })
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('opens window on View Details button click', async ({ page }) => {
    const contributeButton = await page.getByRole('button', { name: 'Learn more about Committee' })
    await contributeButton.waitFor({ state: 'visible' })
    await contributeButton.click()
    await expect(page).toHaveURL('/committees/committee_1')
  })

  test('breadcrumb renders correct segments on /committees', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Committees'])
  })
})
