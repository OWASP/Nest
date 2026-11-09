import { iphone13Chromium } from '@e2e/helpers/devices'
import { expectBreadCrumbsToBeVisible, getGapBelowSearch } from '@e2e/helpers/expects'
import { mockChapterData } from '@mockData/mockChapterData'
import { test, expect } from '@playwright/test'

test.describe('Chapters Page', () => {
  test.beforeEach(async ({ page }) => {
    // Block OpenStreetMap tile requests; the chapters page renders a map but these
    // tests do not assert on it, and external tile loads add latency and flakiness.
    await page.route('https://*.tile.openstreetmap.org/**', (route) => route.abort())

    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockChapterData.chapters,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/chapters', { waitUntil: 'domcontentloaded' })
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
    await page.goto('/chapters', { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('No chapters found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = page.getByRole('button', { name: '2' })
    await nextPageButton.waitFor({ state: 'visible' })
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('opens window on View Details button click', async ({ page }) => {
    const contributeButton = page.getByRole('button', { name: 'View Details' })
    await contributeButton.waitFor({ state: 'visible' })
    await contributeButton.click()
    await expect(page).toHaveURL('chapters/chapter_1')
  })

  // On desktop the country filter sits inline beside search, so only the mobile layout has a gap
  test.describe('mobile layout', () => {
    test.use({ viewport: iphone13Chromium.viewport })

    test('leaves a 16px gap between search and the filter row', async ({ page }) => {
      const countryFilter = page
        .locator('div.h-12', { has: page.getByRole('combobox', { name: 'Country' }) })
        .filter({ visible: true })
      expect(await getGapBelowSearch(page, countryFilter)).toBe(16)
    })
  })

  test('breadcrumb renders correct segments on /chapters', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Chapters'])
  })
})
