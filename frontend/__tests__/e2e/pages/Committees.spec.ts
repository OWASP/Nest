import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockCommitteeData } from '@mockData/mockCommitteeData'
import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Committees Page', () => {
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
          hits: mockCommitteeData.committees,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/committees', { timeout: 25000 })
  })
  test.afterAll(async () => {
    await context.close()
  })
  test('renders committee data correctly', async () => {
    await expect(page.getByRole('link', { name: 'Committee 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Committee 1')).toBeVisible()
    await expect(page.getByRole('link', { name: "Sam Stepanyan's avatar" })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Learn more about Committee' })).toBeVisible()
  })

  test('handles page change correctly', async () => {
    const nextPageButton = page.getByRole('button', { name: '2' })
    await nextPageButton.waitFor({ state: 'visible' })
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('breadcrumb renders correct segments on /committees', async () => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Committees'])
  })
  test('opens window on View Details button click', async () => {
    const contributeButton = page.getByRole('button', { name: 'Learn more about Committee' })
    await contributeButton.waitFor({ state: 'visible' })
    await contributeButton.click()
    await expect(page).toHaveURL('/committees/committee_1')
  })
  test('displays "No committees found" when there are no committees', async () => {
    await page.goto('/committees')
    await page.unroute('**/idx/')
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await expect(page.getByText('No committees found')).toBeVisible()
  })
})
