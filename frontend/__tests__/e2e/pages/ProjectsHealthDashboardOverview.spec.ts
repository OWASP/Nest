import { test, expect } from '@playwright/test'
import { mockProjectsDashboardOverviewData } from '@unit/data/mockProjectsDashboardOverviewData'
import millify from 'millify'

test.describe('Projects Health Dashboard Overview', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/auth/login/**', async (route) => {
      await route.fulfill({
        status: 200,
        json: {
          data: {
            session: {
              user: {
                login: 'testuser',
                accessToken: 'test-access-token',
              },
            },
          },
        },
      })
    })
    await page.route('**/graphql/', async (route, request) => {
      const postData = request.postDataJSON()
      switch (postData.operationName) {
        case 'GetUser':
          await route.fulfill({
            status: 200,
            json: { data: { user: mockProjectsDashboardOverviewData.user } },
          })
          break
        case 'SyncDjangoSession':
          await route.fulfill({
            status: 200,
            json: { data: { githubAuth: mockProjectsDashboardOverviewData.githubAuth } },
          })
          break
        default:
          await route.fulfill({
            status: 200,
            json: {
              data: { projectHealthStats: mockProjectsDashboardOverviewData.projectHealthStats },
            },
          })
          break
      }
    })
    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])
    await page.goto('/projects/dashboard', { timeout: 100000 })
  })
  test('shows 404 page if not authenticated', async ({ page }) => {
    await expect(page.getByText('404', { exact: true })).toBeVisible()
  })
  test('renders project health stats', async ({ page }) => {
    await expect(page.getByText('Project Health Dashboard Overview')).toBeVisible({
      timeout: 10000,
    })

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
