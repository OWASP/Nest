import { test, expect } from '@playwright/test'
import { mockContributeData } from '@unit/data/mockContributeData'

test.describe('Contribute Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockContributeData.issues,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/projects/contribute')
  })

  test('renders issue data correctly', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Contribution 1' })).toBeVisible()
    await expect(page.getByText('4 months ago')).toBeVisible()
    await expect(page.getByRole('link', { name: 'Owasp Nest' })).toBeVisible()
    await expect(page.getByText('This is a summary of Contribution 1')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Read More' })).toBeVisible()
  })

  test('displays "No Issues found" when there are no issues', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], totalPages: 0 }),
      })
    })
    await page.goto('/projects/contribute')
    await expect(page.getByText('No issues found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = await page.getByRole('button', { name: '2' })
    await nextPageButton.click()
    expect(await page.url()).toContain('page=2')
  })

  test('opens dialog on View Details button click', async ({ page }) => {
    const contributeButton = page.getByRole('button', { name: 'Read More' }).first()
    await contributeButton.click()
    const dialog = page.getByRole('dialog')
    await expect(dialog).toBeVisible()
    await expect(
      dialog.getByText(
        'The issue summary and the recommended steps to address it have been generated by AI'
      )
    ).toBeVisible()
    await expect(dialog.getByRole('link', { name: 'View Issue' })).toBeVisible()
  })

  test('closes dialog on close button click', async ({ page }) => {
    const contributeButton = await page.getByRole('button', { name: 'Read More' })
    await expect(contributeButton).toBeVisible()
    await contributeButton.click()
    const CloseButton = await page.getByRole('button', { name: 'close-modal' })
    await expect(CloseButton).toBeVisible()
    await CloseButton.click()
    await expect(contributeButton).toBeVisible()
  })
})
