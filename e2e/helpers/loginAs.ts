import { Page } from '@playwright/test'

export async function loginAs(page: Page, username: string) {
  const response = await page.request.post('/e2e/login/', {
    data: { username },
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok()) {
    throw new Error(`e2e login failed: ${response.status()} ${await response.text()}`)
  }
}

export async function setNextAuthSession(
  page: Page,
  username: string,
  options?: { maxAge?: number }
) {
  const response = await page.request.post('/api/e2e/session', {
    data: { username, ...(options?.maxAge === undefined ? {} : { maxAge: options.maxAge }) },
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok()) {
    throw new Error(`e2e nextauth session failed: ${response.status()} ${await response.text()}`)
  }
}

export async function setInvalidNextAuthSession(page: Page) {
  await page.context().addCookies([
    {
      name: 'next-auth.session-token',
      path: '/',
      url: process.env.FRONTEND_URL || 'http://localhost:3000',
      value: 'invalid-session-token',
    },
  ])
}

export async function loginAsPage(page: Page, username: string) {
  await loginAs(page, username)
  await setNextAuthSession(page, username)
}
