import { test, expect } from '@playwright/test'
import mockProjectData from '@unit/data/mockProjectData'

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
    await page.goto('/projects')
  })

  test('renders project data correctly', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Project 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Project 1')).toBeVisible()
    await expect(page.getByRole('button', { name: 'View Details' })).toBeVisible()
  })

  test('displays "No Project found" when there are no project', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/projects')
    await expect(page.getByText('No projects found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = await page.getByRole('button', { name: '2' })
    await nextPageButton.click()
    expect(await page.url()).toContain('page=2')
  })

  test('opens window on View Details button click', async ({ page }) => {
    const contributeButton = await page.getByRole('button', { name: 'View Details' })
    await contributeButton.click()
    expect(await page.url()).toContain('projects/project_1')
  })
})
