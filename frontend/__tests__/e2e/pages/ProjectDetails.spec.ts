import { test, expect } from '@playwright/test'
import { mockProjectDetailsData } from '@unit/data/mockProjectDetailsData'

test.describe('Project Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: {
          data: mockProjectDetailsData,
        },
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
    await page.goto('/projects/test-project', { timeout: 60000 })
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Project' })).toBeVisible()
    await expect(
      page.getByText('An example project showcasing GraphQL and Django integration.')
    ).toBeVisible()
  })

  test('should have project details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Project Details' })).toBeVisible()
    await expect(page.getByText('Last Updated: Feb 7, 2025')).toBeVisible()
    await expect(page.getByText('Level: Lab')).toBeVisible()
    await expect(page.getByText('Leaders: alice, bob')).toBeVisible()
    await expect(page.getByText('URL: https://github.com/')).toBeVisible()
  })

  test('should have project statics block', async ({ page }) => {
    await expect(page.getByText('2.2K Stars')).toBeVisible()
    await expect(page.getByText('10 Forks')).toBeVisible()
    await expect(page.getByText('1.2K Contributors')).toBeVisible()
    await expect(page.getByText('10 Issues')).toBeVisible()
    await expect(page.getByText('3 Repositories')).toBeVisible()
  })

  test('should have project topics', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Topics' })).toBeVisible()
    await expect(page.getByText('graphql', { exact: true })).toBeVisible()
    await expect(page.getByText('django', { exact: true })).toBeVisible()
    await expect(page.getByText('backend')).toBeVisible()
  })

  test('should have project languages', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Languages' })).toBeVisible()
    await expect(page.getByText('Python', { exact: true })).toBeVisible()
    await expect(page.getByText('GraphQL', { exact: true })).toBeVisible()
    await expect(page.getByText('JavaScript', { exact: true })).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 1', exact: true })).toBeVisible()
    await expect(page.getByText('Contributor 1', { exact: true })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 2', exact: true })).toBeVisible()
    await expect(page.getByText('Contributor 2', { exact: true })).toBeVisible()
  })

  test('toggle top contributors', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).click()
    await expect(page.getByRole('button', { name: 'Show less' })).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).click()
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
  })

  test('should have project recent issues', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Fix authentication bug' })).toBeVisible()
    await expect(page.getByText('Feb 5, 2025')).toBeVisible()
    await expect(page.getByText('test-repo')).toBeVisible()
  })

  test('should have project recent releases', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'V1.2.0' })).toBeVisible()
    await expect(page.getByText('Jan 20, 2025')).toBeVisible()
  })

  test('should have project recent milestones', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'v2.0.0 Release' })).toBeVisible()
    await expect(page.getByText('Mar 1, 2025')).toBeVisible()
    await expect(page.getByText('Project Repo 1')).toBeVisible()
  })

  test('should display recent pull requests section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    await expect(page.getByText('Test Pull Request 1')).toBeVisible()
    await expect(page.getByText('Test Pull Request 2')).toBeVisible()
  })

  test('should have project repositories', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Repositories' })).toBeVisible()
    await expect(page.getByText('Repo One')).toBeVisible()
    await expect(page.getByText('Stars95')).toBeVisible()
    await expect(page.getByText('Forks12')).toBeVisible()
    await expect(page.getByText('Contributors40')).toBeVisible()
    await expect(page.getByText('Issues6')).toBeVisible()
    await expect(page.getByText('Repo Two')).toBeVisible()
    await expect(page.getByText('Stars60')).toBeVisible()
    await expect(page.getByText('Forks8')).toBeVisible()
    await expect(page.getByText('Contributors30')).toBeVisible()
    await expect(page.getByText('Issues3', { exact: true })).toBeVisible()

    await page.getByText('Repo One').click()
    await expect(page).toHaveURL('organizations/OWASP/repositories/repo-1')
  })

  test('should display health metrics section', async ({ page }) => {
    await expect(page.getByText('Issues Trend')).toBeVisible()
    await expect(page.getByText('Pull Requests Trend')).toBeVisible()
    await expect(page.getByText('Stars Trend')).toBeVisible()
    await expect(page.getByText('Forks Trend')).toBeVisible()
    await expect(page.getByText('Days Since Last Commit and Release')).toBeVisible()
  })
})
