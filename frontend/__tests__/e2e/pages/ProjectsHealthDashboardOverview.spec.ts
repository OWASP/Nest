import { test, expect } from '@playwright/test'
import { mockProjectsDashboardOverviewData } from '@unit/data/mockProjectsDashboardOverviewData'
import millify from 'millify'

test.describe('Projects Health Dashboard Overview', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/auth/session', async (route) => {
      await route.fulfill({
        status: 200,
        json: {
          user: {
            login: 'testuser',
          },
          accessToken: 'test-access-token',
          expires: '2125-08-28T01:33:56.550Z',
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
      {
        name: 'nest.session-id',
        value: 'test-session-id',
        domain: 'localhost',
        path: '/',
      },
      {
        name: 'next-auth.csrf-token',
        value: 'test-csrf-token',
        domain: 'localhost',
        path: '/',
      },
      {
        name: 'next-auth.callback-url',
        value: '/',
        domain: 'localhost',
        path: '/',
      },
      {
        name: 'next-auth.session-token',
        value: 'test-session-token',
        domain: 'localhost',
        path: '/',
      },
    ])
    await page.goto('/projects/dashboard', { timeout: 100000 })
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
