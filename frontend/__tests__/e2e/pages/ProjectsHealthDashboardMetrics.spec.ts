import { mockDashboardCookies } from '@e2e/helpers/mockDashboardCookies'
import { mockHealthMetricsData } from '@mockData/mockProjectsHealthMetricsData'
import { test, expect, Page, BrowserContext } from '@playwright/test'
test.describe.serial('Projects Health Dashboard Metrics', () => {
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
    await mockDashboardCookies(page, mockHealthMetricsData, false)
    await page.goto('/projects/dashboard/metrics', { timeout: 25000 })
    await expect(page.getByText('404')).toBeVisible()
    await expect(page.getByText("Sorry, the page you're looking for doesn't exist.")).toBeVisible()
  })

  test('renders page headers', async () => {
    await mockDashboardCookies(page, mockHealthMetricsData, true)
    await page.goto('/projects/dashboard/metrics', { timeout: 25000 })
    await expect(page.getByRole('heading', { name: 'Project Health Metrics' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Filter By' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Score' })).toBeVisible()
  })

  test('renders health metrics data', async () => {
    await mockDashboardCookies(page, mockHealthMetricsData, true)
    await page.goto('/projects/dashboard/metrics', { timeout: 25000 })
    const firstMetric = mockHealthMetricsData.projectHealthMetrics[0]
    const metricsLink = page
      .getByRole('link')
      .filter({
        has: page.getByText(firstMetric.projectName),
      })
      .first()

    await expect(metricsLink).toBeVisible({ timeout: 10000 })
    await expect(
      page
        .getByRole('link')
        .filter({
          has: page.getByText(firstMetric.starsCount.toString()),
        })
        .first()
    ).toBeVisible()
    await expect(
      page
        .getByRole('link')
        .filter({
          has: page.getByText(firstMetric.forksCount.toString()),
        })
        .first()
    ).toBeVisible()
    await expect(
      page
        .getByRole('link')
        .filter({
          has: page.getByText(firstMetric.contributorsCount.toString()),
        })
        .first()
    ).toBeVisible()
    await expect(
      page
        .getByRole('link')
        .filter({
          has: page.getByText(
            new Date(firstMetric.createdAt).toLocaleString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })
          ),
        })
        .first()
    ).toBeVisible()
    await expect(
      page
        .getByRole('link')
        .filter({
          has: page.getByText(firstMetric.score.toString()),
        })
        .first()
    ).toBeVisible()
  })
})
