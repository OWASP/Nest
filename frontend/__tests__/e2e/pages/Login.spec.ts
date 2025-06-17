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
    await page.goto('/auth/login')

    const button = page.getByRole('button', { name: /sign in with github/i })
    await expect(button).toBeVisible()
  })

  test('shows spinner while loading session', async ({ page }) => {
    await page.route('**/auth/session', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 500))
      await route.fulfill({
        status: 200,
        body: JSON.stringify({}),
      })
    })

    await page.goto('/auth/login')

    await expect(page.getByText(/checking session/i)).toBeVisible()
  })

  test('shows message if authentication is disabled', async ({ page }) => {
    await page.goto('/auth/login')

    const disabledMessage = page.getByText(/authentication is not enabled/i)
    await expect(disabledMessage).toBeVisible()
  })
})
