import { mockHomeData } from '@e2e/data/mockHomeData'
import { test, expect } from '@playwright/test'

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify(mockHomeData),
      })
    })

    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
        httpOnly: false,
        secure: false,
        sameSite: 'Lax',
      },
    ])
  })

  test('displays GitHub login button when unauthenticated', async ({ page }) => {
    await page.goto('/login')

    const button = page.getByRole('button', { name: /sign in with github/i })
    await expect(button).toBeVisible()
  })

  test('displays loading spinner when logging in', async ({ page }) => {
    await page.goto('/login')

    const button = page.getByRole('button', { name: /sign in with github/i })
    await button.click()
    await expect(page).toHaveURL(/github\.com/)
  })
  test('shows spinner while loading session', async ({ page }) => {
    await page.route('**/api/auth/session', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 500))
      await route.fulfill({
        status: 200,
        body: JSON.stringify({}),
      })
    })

    await page.goto('/login')

    await expect(page.getByText(/checking session/i)).toBeVisible()
  })
})
