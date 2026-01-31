import { mockDashboardCookies } from '@e2e/helpers/mockDashboardCookies'
import { mockProjectsDashboardMetricsDetailsData } from '@mockData/mockProjectsDashboardMetricsDetailsData'
import { expect, test, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Project Health Metrics Details Page', () => {
  let page: Page
  let context: BrowserContext
  test.beforeAll(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      baseURL: testInfo.project.use.baseURL,
    })
    page = await context.newPage()
  })
  test.afterAll(async () => {
    await context.close()
  })
  test('renders 404 when user is not OWASP staff', async () => {
    await mockDashboardCookies(page, mockProjectsDashboardMetricsDetailsData, false)
    await page.goto('/projects/dashboard/metrics/test-project', { timeout: 25000 })
    await expect(page.getByText('404')).toBeVisible()
    await expect(page.getByText("Sorry, the page you're looking for doesn't exist.")).toBeVisible()
  })
  test('renders project health metrics details', async () => {
    await mockDashboardCookies(page, mockProjectsDashboardMetricsDetailsData, true)
    await page.goto('/projects/dashboard/metrics/nest', { timeout: 25000 })
    const metricsLatest = mockProjectsDashboardMetricsDetailsData.project.healthMetricsLatest
    const headers = [
      'Days Metrics',
      'Issues',
      'Stars',
      'Forks',
      'Contributors',
      'Releases',
      'Open Pull Requests',
      'Health',
      'Score',
    ]
    await expect(page.getByText(metricsLatest.projectName)).toBeVisible()
    await expect(page.getByText(metricsLatest.score.toString())).toBeVisible()
    for (const header of headers) {
      await expect(page.getByText(header, { exact: true })).toBeVisible()
    }
  })
})
