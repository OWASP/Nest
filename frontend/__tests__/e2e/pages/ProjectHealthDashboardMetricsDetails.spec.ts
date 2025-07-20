import { expect, test } from '@playwright/test'
import { mockProjectsDashboardMetricsDetailsData } from '@unit/data/mockProjectsDashboardMetricsDetailsData'

test.describe('Project Health Metrics Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockProjectsDashboardMetricsDetailsData },
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
    await page.goto('/projects/dashboard/metrics/test-project')
  })

  test('renders project health metrics details', async ({ page }) => {
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
      await expect(page.getByText(header).all()).toBeGreaterThan(0)
    }
  })
})
