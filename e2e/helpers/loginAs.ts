import { Page } from '@playwright/test'

async function postJson(page: Page, url: string, data: object, errorLabel: string) {
  const response = await page.request.post(url, {
    data,
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok()) {
    throw new Error(`${errorLabel}: ${response.status()} ${await response.text()}`)
  }
}

export async function loginAs(page: Page, username: string) {
  await postJson(page, '/e2e/login/', { username }, 'e2e login failed')
}

export async function setNextAuthSession(page: Page, username: string, maxAge?: number) {
  await postJson(
    page,
    '/api/e2e/session',
    maxAge === undefined ? { username } : { username, maxAge },
    'e2e nextauth session failed'
  )
}

export async function setInvalidNextAuthSession(page: Page) {
  const frontend = new URL(process.env.FRONTEND_URL)
  await page.context().addCookies([
    {
      domain: frontend.hostname,
      name: 'next-auth.session-token',
      path: '/',
      value: 'invalid-session-token',
    },
  ])
}

export async function loginAsPage(page: Page, username: string) {
  await loginAs(page, username)
  await setNextAuthSession(page, username)
}
