import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockChapterData } from '@mockData/mockChapterData'
import { test, expect } from '@playwright/test'

test.describe('Chapters Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockChapterData.chapters,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/chapters', { timeout: 25000 })
  })

  test('renders chapter data correctly', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Chapter 1' })).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('This is a summary of Chapter')).toBeVisible()
    await expect(page.getByRole('link', { name: "Isanori Sakanashi's avatar" })).toBeVisible()
    await expect(page.getByRole('button', { name: 'View Details' })).toBeVisible()
  })

  test('displays "No chapters found" when there are no chapters', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/chapters')
    await expect(page.getByText('No chapters found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = await page.getByRole('button', { name: '2' })
    await nextPageButton.waitFor({ state: 'visible' }) // Ensure button is visible
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('opens window on View Details button click', async ({ page }) => {
    const contributeButton = await page.getByRole('button', { name: 'View Details' })
    await contributeButton.waitFor({ state: 'visible' })
    await contributeButton.click()
    await expect(page).toHaveURL('chapters/chapter_1')
  })

  test('breadcrumb renders correct segments on /chapters', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Chapters'])
  })
})
