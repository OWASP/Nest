import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { test, expect } from '@playwright/test'

const mockPrograms = [
  {
    key: 'program_1',
    name: 'Program 1',
    description: 'This is a summary of Program 1.',
    startedAt: '2025-01-01T00:00:00Z',
    endedAt: '2025-12-31T00:00:00Z',
    status: 'PUBLISHED',
    modules: ['Module A', 'Module B'],
  },
]

test.describe('Mentorship Programs Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: mockPrograms, nbPages: 1 }),
      })
    })
    await page.goto('/mentorship/programs', { timeout: 25000 })
  })

  test('renders program card from mock data', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Program 1' })).toBeVisible()
    await expect(page.getByText('This is a summary of Program 1.')).toBeVisible()
  })

  test('program card link navigates to program details', async ({ page }) => {
    const programLink = page.getByRole('link', { name: 'Program 1' })
    await programLink.waitFor({ state: 'visible' })
    await expect(programLink).toHaveAttribute('href', '/mentorship/programs/program_1')
    await programLink.click()
    await expect(page).toHaveURL('/mentorship/programs/program_1')
  })

  test('search input is visible', async ({ page }) => {
    await expect(page.getByPlaceholder('Search for programs...')).toBeVisible()
  })

  test('displays "No programs found" when there are no programs', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/mentorship/programs', { timeout: 25000 })
    await expect(page.getByText('No programs found')).toBeVisible()
  })

  test('breadcrumb renders correct segments on /mentorship/programs', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Mentorship'])
  })
})
