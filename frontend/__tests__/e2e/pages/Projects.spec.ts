import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import mockProjectData from '@mockData/mockProjectData'
import { test, expect } from '@playwright/test'

test.describe('Projects Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockProjectData.projects,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/projects', { timeout: 25000 })
  })

  test('renders project data correctly', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Project 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Project 1')).toBeVisible()
    await expect(page.getByRole('button', { name: 'View Details' })).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = page.getByRole('button', { name: '2' })
    await nextPageButton.waitFor({ state: 'visible' })
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('breadcrumb renders correct segments on /projects', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Projects'])
  })

  test('opens window on View Details button click', async ({ page }) => {
    const contributeButton = page.getByRole('button', { name: 'View Details' })
    await contributeButton.waitFor({ state: 'visible' })
    await contributeButton.click()
    await expect(page).toHaveURL('projects/project_1')
  })

  test('displays "No Projects found" when there are no projects', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/projects')
    await expect(page.getByText('No projects found')).toBeVisible()
  })
})
