import { test, expect } from '@playwright/test'
import { mockCommitteeData } from '@unit/data/mockCommitteeData'

test.describe('committees Page Component', () => {
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
  })

  test('renders committee data correctly', async ({ page }) => {
    await page.goto('/committees')
    await expect(page.getByRole('link', { name: 'Committee 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Committee 1')).toBeVisible()
    await expect(page.getByRole('link', { name: "Sam Stepanyan's avatar" })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Learn more about Committee' })).toBeVisible()
  })

  test('displays "No committees found" when there are no committees', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], totalPages: 0 }),
      })
    })

    await page.goto('/committees')
    await expect(page.getByText('No committees Found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    await page.goto('/committees')
    const nextPageButton = await page.getByRole('button', { name: '2' })
    await nextPageButton.click()
    expect(await page.url()).toContain('page=2')
  })

  test('opens window on View Details button click', async ({ page }) => {
    await page.goto('/committees')
    const contributeButton = await page.getByRole('button', { name: 'Learn more about Committee' })
    await contributeButton.click()
    expect(await page.url()).toContain('committees/committee_1')
  })
})
