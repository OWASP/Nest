import { mockDashboardCookies } from '@e2e/helpers/mockDashboardCookies'
import { mockProjectsDashboardOverviewData } from '@mockData/mockProjectsDashboardOverviewData'
import { test, expect, Page, BrowserContext } from '@playwright/test'
import millify from 'millify'

test.describe('Projects Health Dashboard Overview', () => {
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
    await mockDashboardCookies(page, mockProjectsDashboardOverviewData, false)
    await page.goto('/projects/dashboard', { timeout: 25000 })
    await expect(page.getByText('404')).toBeVisible()
    await expect(page.getByText("Sorry, the page you're looking for doesn't exist.")).toBeVisible()
  })

  test('renders project health stats', async () => {
    await mockDashboardCookies(page, mockProjectsDashboardOverviewData, true)
    await page.goto('/projects/dashboard', { timeout: 25000 })
    await expect(page.getByText('Project Health Dashboard Overview')).toBeVisible()

    // Check for healthy projects
    await expect(
      page.getByText(
        mockProjectsDashboardOverviewData.projectHealthStats.projectsCountHealthy.toString()
      )
    ).toBeVisible()
    // Check for projects needing attention
    await expect(
      page.getByText(
        mockProjectsDashboardOverviewData.projectHealthStats.projectsCountNeedAttention.toString()
      )
    ).toBeVisible()
    // Check for unhealthy projects
    await expect(
      page.getByText(
        mockProjectsDashboardOverviewData.projectHealthStats.projectsCountUnhealthy.toString()
      )
    ).toBeVisible()
    // Check for average score
    await expect(
      page.getByText(mockProjectsDashboardOverviewData.projectHealthStats.averageScore.toFixed(1))
    ).toBeVisible()
    // Check for total contributors
    await expect(
      page.getByText(
        millify(mockProjectsDashboardOverviewData.projectHealthStats.totalContributors)
      )
    ).toBeVisible()
    // Check for total forks
    await expect(
      page.getByText(millify(mockProjectsDashboardOverviewData.projectHealthStats.totalForks))
    ).toBeVisible()
    // Check for total stars
    await expect(
      page.getByText(millify(mockProjectsDashboardOverviewData.projectHealthStats.totalStars))
    ).toBeVisible()
  })
})
