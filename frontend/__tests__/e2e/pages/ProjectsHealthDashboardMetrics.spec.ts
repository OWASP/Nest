import { mockDashboardCookies } from '@e2e/helpers/mockDashboardCookies'
import { test, expect } from '@playwright/test'
import { mockHealthMetricsData } from '@unit/data/mockProjectsHealthMetricsData'
test.describe('Projects Health Dashboard Metrics', () => {
  test('renders 404 when user is not OWASP staff', async ({ page }) => {
    await mockDashboardCookies(page, mockHealthMetricsData, false)
    await page.goto('/projects/dashboard/metrics')
    await expect(page.getByText('404')).toBeVisible()
    await expect(page.getByText('This page could not be found.')).toBeVisible()
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
    await expect(page.getByText(firstMetric.projectName)).toBeVisible()
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
