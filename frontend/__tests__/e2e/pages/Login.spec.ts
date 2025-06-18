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

  test('shows message authentication is disabled', async ({ page }) => {
    await page.goto('/auth/login')

    const disabledMessage = page.getByText(/authentication is disabled/i)
    await expect(disabledMessage).toBeVisible()
  })
})
