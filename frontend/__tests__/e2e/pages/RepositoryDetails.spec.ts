import { test, expect, Page } from '@playwright/test'
import { mockRepositoryData } from '@unit/data/mockRepositoryData'

function getFirstHeading(page: Page, name: string) {
  return page.getByRole('heading', { name }).first()
}

test.describe('Repository Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockRepositoryData },
      })
    })
    await page.goto('/repositories/test-repository')
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Repo' })).toBeVisible()
    await expect(page.getByText('A sample test repository')).toBeVisible()
  })

  test('should have repository details block', async ({ page }) => {
    await expect(getFirstHeading(page, 'Repository Details')).toBeVisible()
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
    await expect(getFirstHeading(page, 'Topics')).toBeVisible()
    await expect(page.getByText('JavaScript', { exact: true })).toBeVisible()
    await expect(page.getByText('TypeScript', { exact: true })).toBeVisible()
  })

  test('should have languages', async ({ page }) => {
    await expect(getFirstHeading(page, 'Languages')).toBeVisible()
    await expect(page.getByText('web', { exact: true })).toBeVisible()
    await expect(page.getByText('security', { exact: true })).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(getFirstHeading(page, 'Top Contributors')).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 1' })).toBeVisible()
    await expect(page.getByText('Contributor 1')).toBeVisible()
    await expect(page.getByText('30 Contributions')).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 2' })).toBeVisible()
    await expect(page.getByText('Contributor 2')).toBeVisible()
    await expect(page.getByText('29 Contributions')).toBeVisible()
  })

  test('toggle top contributors', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).click()
    await expect(page.getByRole('button', { name: 'Show less' })).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).click()
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
  })

  test('should have recent issues', async ({ page }) => {
    await expect(getFirstHeading(page, 'Recent Issues')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Bug fix required' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Test User 1' })).toBeVisible()
    await expect(page.getByText('Jan 2, 2024')).toBeVisible()
    await expect(page.getByText('4 comments')).toBeVisible()
  })

  test('should have recent releases', async ({ page }) => {
    await expect(getFirstHeading(page, 'Recent Releases')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'v1.0.0' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Test User 2' })).toBeVisible()
    await expect(page.getByText('Jan 1, 2024', { exact: true })).toBeVisible()
  })
})
