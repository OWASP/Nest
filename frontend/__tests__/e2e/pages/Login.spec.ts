import { test, expect } from '@playwright/test'

test.describe('Login Page', () => {
  test('shows message authentication is enabled', async ({ page }) => {
    await page.goto('/auth/login', { timeout: 120000 })

    const welcomeMessage = page.getByText('Welcome back')
    const gitHubLoginButton = page.getByRole('button', { name: 'Sign In with GitHub' })
    const gitHubMessage = page.getByText('Sign in with your GitHub account to continue')
    await expect(welcomeMessage).toBeVisible()
    await expect(gitHubLoginButton).toBeVisible()
    await expect(gitHubMessage).toBeVisible()
  })
})
