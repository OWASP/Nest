import { loginAs, loginAsPage } from '@e2e/helpers/loginAs'
import { test, expect } from '@playwright/test'

const MY_PROGRAMS_QUERY = `
  query {
    myPrograms {
      currentPage
      totalPages
      programs { key }
    }
  }
`

test.describe('My Mentorship', () => {
  test('redirects unauthenticated users to login', async ({ page }) => {
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/auth\/login/)
  })

  test('allows myPrograms GraphQL after e2e login', async ({ page }) => {
    await loginAs(page, 'e2e-mentor')

    const csrfResponse = await page.request.get('/csrf/')
    const { csrftoken } = await csrfResponse.json()
    const response = await page.request.post('/graphql/', {
      data: { query: MY_PROGRAMS_QUERY },
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
    })
    const body = await response.json()

    expect(body.errors).toBeUndefined()
    expect(body.data.myPrograms).toBeTruthy()
  })

  test('renders My Mentorship after e2e page login', async ({ page }) => {
    await loginAsPage(page, 'e2e-mentor')
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page).not.toHaveURL(/\/auth\/login/)
    await expect(page.getByRole('heading', { name: 'My Mentorship' })).toBeVisible()
    await expect(page.getByText('No programs found')).toBeVisible()
  })
})
