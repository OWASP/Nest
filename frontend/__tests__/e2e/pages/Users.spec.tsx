import { test, expect } from '@playwright/test'
import { mockUserData } from '@unit/data/mockUserData'

test.describe('Users Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          hits: mockUserData.users,
          nbPages: 2,
        }),
      })
    })
    await page.goto('/community/users')
  })

  test('renders user data correctly', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'John Doe John Doe OWASP View' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Jane Smith Jane Smith' })).toBeVisible()
  })

  test('displays "No user found" when there are no users', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/community/users')
    await expect(page.getByText('No Users Found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = await page.getByRole('button', { name: '2' })
    await nextPageButton.click()
    expect(await page.url()).toContain('page=2')
  })

  test('opens window on button click', async ({ page }) => {
    const userButton = await page.getByRole('button', {
      name: 'John Doe John Doe OWASP View',
    })
    await userButton.click()
    expect(await page.url()).toContain('community/users/user_1')
  })
})
