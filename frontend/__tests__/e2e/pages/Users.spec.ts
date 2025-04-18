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
    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])
    await page.goto('/members')
  })

  test('renders user data correctly', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'John Doe' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Jane Smith' })).toBeVisible()
  })

  test('displays "No user found" when there are no users', async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ hits: [], nbPages: 0 }),
      })
    })
    await page.goto('/members')
    await expect(page.getByText('No Users Found')).toBeVisible()
  })

  test('handles page change correctly', async ({ page }) => {
    const nextPageButton = await page.getByRole('button', { name: '2', exact: true })
    await nextPageButton.waitFor({ state: 'visible' })
    await nextPageButton.click()
    await expect(page).toHaveURL(/page=2/)
  })

  test('opens window on button click', async ({ page }) => {
    const userButton = await page.getByRole('button', { name: 'John Doe' })
    await userButton.waitFor({ state: 'visible' })
    await userButton.click()
    await expect(page).toHaveURL('/members/user_1')
  })

  test('displays followers and repositories counts correctly', async ({ page }) => {
    const userButton = await page.getByRole('button', { name: 'John Doe' })
    await userButton.waitFor({ state: 'visible' })
    await expect(page.getByText('1k')).toBeVisible()
    await expect(page.getByText('2k')).toBeVisible()
  })
  test('breadcrumb renders correct segments on /members', async ({ page }) => {
    const breadcrumb = page.locator('[aria-label="breadcrumb"]')
    await expect(breadcrumb).toBeVisible()
    await expect(breadcrumb.getByText('Home')).toBeVisible()
    await expect(breadcrumb.getByText('Members')).toBeVisible()
  })
})
