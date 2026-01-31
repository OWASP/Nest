import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockOrganizationData } from '@mockData/mockOrganizationData'
import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Organization Page', () => {
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
          hits: mockOrganizationData.hits,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/organizations', { timeout: 25000 })
  })
  test.afterAll(async () => {
    await context.close()
  })

  test('renders organization data correctly', async () => {
    await expect(page.getByRole('heading', { name: 'Test Organization' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Another Organization' })).toBeVisible()

    const viewDetailsButtons = page.getByRole('button', { name: 'View Profile' })
    await expect(viewDetailsButtons).toHaveCount(2)
  })

  test('navigation to organization details works', async () => {
    await page.getByRole('button', { name: 'View Profile' }).first().click()
    expect(await page.url()).toContain('organizations')
  })

  test('displays followers and repositories counts correctly', async () => {
    await expect(page.getByText('1k')).toBeVisible()
    await expect(page.getByText('1.5k')).toBeVisible()
  })

  test('breadcrumb renders correct segments on /organizations', async () => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Organizations'])
  })
})
