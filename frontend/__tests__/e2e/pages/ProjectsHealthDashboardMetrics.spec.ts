import { test, expect } from '@playwright/test'
import { mockHealthMetricsData } from '@unit/data/mockProjectsHealthMetricsData'

test.describe('Projects Health Dashboard Metrics', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockHealthMetricsData },
      })
    })
    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])
    await page.goto('/projects/dashboard/metrics', { timeout: 60000 })
  })
  test('renders page headers', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Project Health Metrics' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Filter By' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Score' })).toBeVisible()
  })

  test('renders health metrics data', async ({ page }) => {
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
