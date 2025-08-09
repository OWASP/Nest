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

  test('shows message authentication is enabled', async ({ page }) => {
    await page.goto('/auth/login')

    const welcomeMessage = page.getByText('Welcome back')
    const gitHubLoginButton = page.getByRole('button', { name: 'Sign In with GitHub' })
    const gitHubMessage = page.getByText('Sign in with your GitHub account to continue')
    await expect(welcomeMessage).toBeVisible()
    await expect(gitHubLoginButton).toBeVisible()
    await expect(gitHubMessage).toBeVisible()
  })
})
