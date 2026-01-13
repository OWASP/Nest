import { mockDashboardCookies } from '@e2e/helpers/mockDashboardCookies'
import { mockHealthMetricsData } from '@mockData/mockProjectsHealthMetricsData'
import { test, expect } from '@playwright/test'
test.describe('Projects Health Dashboard Metrics', () => {
  test('renders 404 when user is not OWASP staff', async ({ page }) => {
    await mockDashboardCookies(page, mockHealthMetricsData, false)
    await page.goto('/projects/dashboard/metrics')
    await expect(page.getByText('404')).toBeVisible()
    await expect(page.getByText("Sorry, the page you're looking for doesn't exist.")).toBeVisible()
  })

  test('renders page headers', async ({ page }) => {
    await mockDashboardCookies(page, mockHealthMetricsData, true)
    await page.goto('/projects/dashboard/metrics')
    await expect(page.getByRole('heading', { name: 'Project Health Metrics' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Filter By' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Score' })).toBeVisible()
  })

  test('renders health metrics data', async ({ page }) => {
    await mockDashboardCookies(page, mockHealthMetricsData, true)
    await page.goto('/projects/dashboard/metrics')
    const firstMetric = mockHealthMetricsData.projectHealthMetrics[0]
    await expect(page.getByText(firstMetric.projectName)).toBeVisible({ timeout: 10000 })
    await expect(page.getByText(firstMetric.starsCount.toString())).toBeVisible()
    await expect(page.getByText(firstMetric.forksCount.toString())).toBeVisible()
    await expect(page.getByText(firstMetric.contributorsCount.toString())).toBeVisible()
    await expect(
      page.getByText(
        new Date(firstMetric.createdAt).toLocaleString('default', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })
      )
    ).toBeVisible()
    await expect(page.getByText(firstMetric.score.toString())).toBeVisible()
  })
})
