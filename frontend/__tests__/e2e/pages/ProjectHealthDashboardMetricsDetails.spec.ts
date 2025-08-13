import { mockDashboardCookies } from '@e2e/helpers/mockDashboardCookies'
import { expect, test } from '@playwright/test'
import { mockProjectsDashboardMetricsDetailsData } from '@unit/data/mockProjectsDashboardMetricsDetailsData'

test.describe('Project Health Metrics Details Page', () => {
  test('renders 404 when user is not OWASP staff', async ({ page }) => {
    await mockDashboardCookies(page, mockProjectsDashboardMetricsDetailsData, false)
    await page.goto('/projects/dashboard/metrics/test-project')
    await expect(page.getByText('404')).toBeVisible()
    await expect(page.getByText('This page could not be found.')).toBeVisible()
  })
  test('renders project health metrics details', async ({ page }) => {
    await mockDashboardCookies(page, mockProjectsDashboardMetricsDetailsData, true)
    await page.goto('/projects/dashboard/metrics/test-project')
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
