import { test, expect } from '@playwright/test'
import { mockChapterData } from '@unit/data/mockChapterData'

test.describe('ChaptersPage Component', () => {
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
    await page.goto('/chapters')
  })

  test('renders chapter data correctly', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Chapter 1' })).toBeVisible()
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
    await nextPageButton.click()
    expect(await page.url()).toContain('page=2')
  })

  test('opens window on View Details button click', async ({ page }) => {
    const contributeButton = await page.getByRole('button', { name: 'View Details' })
    await contributeButton.click()
    expect(await page.url()).toContain('chapters/chapter_1')
  })
})
