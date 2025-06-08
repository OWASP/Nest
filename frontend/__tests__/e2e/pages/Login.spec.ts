import { mockHomeData } from '@e2e/data/mockHomeData'
import { test, expect } from '@playwright/test'

test.describe('LoginPage - Auth Disabled State', () => {
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

  test('should display auth disabled message if env vars are missing', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByText(/authentication is disabled/i)).toBeVisible()
  })
})
