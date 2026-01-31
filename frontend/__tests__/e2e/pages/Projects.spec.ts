import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import mockProjectData from '@mockData/mockProjectData'
import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Projects Page', () => {
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
          hits: mockProjectData.projects,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/projects', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('renders project data correctly', async () => {
    await expect(page.getByRole('link', { name: 'Project 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Project 1')).toBeVisible()
    await expect(page.getByRole('button', { name: 'View Details' })).toBeVisible()
  })

  test('handles page change correctly', async () => {
    const nextPageButton = page.getByRole('button', { name: '2' })
    await nextPageButton.waitFor({ state: 'visible' })
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('breadcrumb renders correct segments on /projects', async () => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Projects'])
  })
  test('opens window on View Details button click', async () => {
    const contributeButton = page.getByRole('button', { name: 'View Details' })
    await contributeButton.waitFor({ state: 'visible' })
    await contributeButton.click()
    await expect(page).toHaveURL('projects/project_1')
  })
  test('displays "No Projects found" when there are no projects', async () => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/projects')
    await expect(page.getByText('No projects found')).toBeVisible()
  })
})
