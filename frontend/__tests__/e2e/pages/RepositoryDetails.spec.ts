import { test, expect } from '@playwright/test'
import { mockRepositoryData } from '@unit/data/mockRepositoryData'

test.describe('Repository Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockRepositoryData },
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
    await page.goto('organizations/OWASP/repositories/test-repository')
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Repo' })).toBeVisible()
    await expect(page.getByText('A sample test repository')).toBeVisible()
  })

  test('should have repository details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Repository Details' })).toBeVisible()
    await expect(page.getByText('Last Updated: Jan 1, 2024')).toBeVisible()
    await expect(page.getByText('License: MIT')).toBeVisible()
    await expect(page.getByText('Size: 1200 KB')).toBeVisible()
    await expect(page.getByRole('link', { name: 'https://github.com/test-repo' })).toBeVisible()
  })

  test('should have statics block', async ({ page }) => {
    await expect(page.getByText('50K Stars')).toBeVisible()
    await expect(page.getByText('3K Forks')).toBeVisible()
    await expect(page.getByText('5 Contributors')).toBeVisible()
    await expect(page.getByText('2 Issues')).toBeVisible()
    await expect(page.getByText('10 Commits')).toBeVisible()
  })

  test('should have topics', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Topics' })).toBeVisible()
    await expect(page.getByText('JavaScript', { exact: true })).toBeVisible()
    await expect(page.getByText('TypeScript', { exact: true })).toBeVisible()
  })

  test('should have languages', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Languages' })).toBeVisible()
    await expect(page.getByText('web', { exact: true })).toBeVisible()
    await expect(page.getByText('security', { exact: true })).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Contributor 1's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Contributor 1', { exact: true })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Contributor 2's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Contributor 2', { exact: true })).toBeVisible()
  })

  test('toggle top contributors', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).click()
    await expect(page.getByRole('button', { name: 'Show less' })).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).click()
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
  })

  test('should have recent issues', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Bug fix required' })).toBeVisible()
    await expect(page.getByText('Jan 2, 2024')).toBeVisible()
    await expect(page.getByText('test-repo-2')).toBeVisible()
  })

  test('should have recent releases', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'v1.0.0' })).toBeVisible()
    await expect(page.getByText('Jan 1, 2024', { exact: true })).toBeVisible()
  })

  test('should have recent milestones', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'v2.0.0 Release' })).toBeVisible()
    await expect(page.getByText('Mar 1, 2025')).toBeVisible()
    await expect(page.getByText('Repo One')).toBeVisible()
  })

  test('should display recent pull requests section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    await expect(page.getByText('Test Pull Request 1')).toBeVisible()
    await expect(page.getByText('Test Pull Request 2')).toBeVisible()
  })
})
