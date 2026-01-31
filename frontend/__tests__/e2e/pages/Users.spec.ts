import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockUserData } from '@mockData/mockUserData'
import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Users Page', () => {
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
          hits: mockUserData.users,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/members', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('renders user data correctly', async () => {
    await expect(page.getByRole('button', { name: 'John Doe' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Jane Smith' })).toBeVisible()
  })

  test('handles page change correctly', async () => {
    const nextPageButton = page.getByRole('button', { name: 'Go to page 2' })
    await nextPageButton.waitFor({ state: 'visible' })
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('displays followers and repositories counts correctly', async () => {
    const userButton = page.getByRole('button', { name: 'John Doe' })
    await userButton.waitFor({ state: 'visible' })
    await expect(page.getByText('1k')).toBeVisible()
    await expect(page.getByText('2k')).toBeVisible()
  })
  test('breadcrumb renders correct segments on /members', async () => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Members'])
  })
  test('opens window on button click', async () => {
    const userButton = page.getByRole('button', { name: 'John Doe' })
    await userButton.waitFor({ state: 'visible' })
    await userButton.click()
    await expect(page).toHaveURL('/members/user_1')
  })
  test('displays "No user found" when there are no users', async () => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/members')
    await expect(page.getByText('No Users Found')).toBeVisible()
  })
})
