import { test, expect } from '@playwright/test'
import { mockOrganizationData } from '@unit/data/mockOrganizationData'

test.describe('Organization Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockOrganizationData.hits,
          nbPages: 2,
        }),
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
    await page.goto('/organizations')
  })

  test('renders organization data correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Organization' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Another Organization' })).toBeVisible()

    const viewDetailsButtons = page.getByRole('button', { name: 'View Profile' })
    await expect(viewDetailsButtons).toHaveCount(2)
  })

  test('navigation to organization details works', async ({ page }) => {
    await page.getByRole('button', { name: 'View Profile' }).first().click()
    expect(await page.url()).toContain('organizations')
  })

  test('displays followers and repositories counts correctly', async ({ page }) => {
    await expect(page.getByText('1k')).toBeVisible()
    await expect(page.getByText('1.5k')).toBeVisible()
  })
})
