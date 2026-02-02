import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockChapterData } from '@mockData/mockChapterData'
import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Chapters Page', () => {
  let page: Page
  let context: BrowserContext
  test.beforeAll(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      baseURL: testInfo.project.use.baseURL,
    })
    page = await context.newPage()

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
  test.afterAll(async () => {
    await context.close()
  })
  test('renders chapter data correctly', async () => {
    await expect(page.getByRole('link', { name: 'Chapter 1' })).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('This is a summary of Chapter')).toBeVisible()
    await expect(page.getByRole('link', { name: "Isanori Sakanashi's avatar" })).toBeVisible()
    await expect(page.getByRole('button', { name: 'View Details' })).toBeVisible()
  })

  test('handles page change correctly', async () => {
    const nextPageButton = page.getByRole('button', { name: '2' })
    await nextPageButton.waitFor({ state: 'visible' }) // Ensure button is visible
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('breadcrumb renders correct segments on /chapters', async () => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Chapters'])
  })

  test('opens window on View Details button click', async () => {
    const contributeButton = page.getByRole('button', { name: 'View Details' })
    await contributeButton.waitFor({ state: 'visible' })
    await contributeButton.click()
    await expect(page).toHaveURL('chapters/chapter_1')
  })
  test('displays "No chapters found" when there are no chapters', async () => {
    await page.unroute('**/idx/')
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/chapters')
    await expect(page.getByText('No chapters found')).toBeVisible()
  })
})
