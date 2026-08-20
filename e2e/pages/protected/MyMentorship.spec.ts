import {
  loginAs,
  loginAsPage,
  setInvalidNextAuthSession,
  setNextAuthSession,
} from '@e2e/helpers/loginAs'
import { test, expect } from '@playwright/test'
import { Page } from '@playwright/test'

const USER = 'e2e-mentor'

const MY_PROGRAMS_QUERY = `
  query {
    myPrograms {
      currentPage
      totalPages
      programs { key }
    }
  }
`

async function postGraphql(page: Page, query: string) {
  const csrfResponse = await page.request.get('/csrf/')
  const { csrftoken } = await csrfResponse.json()
  const response = await page.request.post('/graphql/', {
    data: { query },
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
  })
  return response.json()
}

test.describe('My Mentorship Page', () => {
  test('redirects unauthenticated users to login', async ({ page }) => {
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/auth\/login/)
  })

  test('allows myPrograms GraphQL after e2e login', async ({ page }) => {
    await loginAs(page, USER)
    const body = await postGraphql(page, MY_PROGRAMS_QUERY)
    expect(body.errors).toBeUndefined()
    expect(body.data.myPrograms).toBeTruthy()
  })

  test('renders heading after e2e page login', async ({ page }) => {
    await loginAsPage(page, USER)
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: 'My Mentorship' })).toBeVisible()
    await expect(page.getByText('No programs found')).toBeVisible()
  })

  test('redirects when NextAuth session cookie is invalid', async ({ page }) => {
    await loginAs(page, USER)
    await setInvalidNextAuthSession(page)
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/auth\/login/)
  })

  test('redirects when NextAuth session cookie is expired', async ({ page }) => {
    await loginAs(page, USER)
    await setNextAuthSession(page, USER, 0)
    await page.goto('/my/mentorship', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/auth\/login/)
  })
})
