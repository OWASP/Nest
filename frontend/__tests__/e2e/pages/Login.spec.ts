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

    test('redirects to / if already authenticated', async ({ page }) => {
        // Set an authenticated session token
        await page.context().addCookies([
            {
                name: 'next-auth.session-token',
                value: 'mocked-session-token',
                domain: 'localhost',
                path: '/',
                httpOnly: true,
                secure: false,
                sameSite: 'Lax',
            },
        ])

        await page.goto('/login')

        // Confirm redirect to home
        await expect(page).toHaveURL('/')
    })

    test('shows spinner while loading session', async ({ page }) => {
        // Simulate a delay in session fetch
        await page.route('**/api/auth/session', async (route) => {
            await new Promise((resolve) => setTimeout(resolve, 500)) // delay 500ms
            await route.fulfill({
                status: 200,
                body: JSON.stringify({}),
            })
        })

        await page.goto('/login')

        await expect(page.getByText(/checking session/i)).toBeVisible()
    })
})
