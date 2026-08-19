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

export async function loginAsPage(page: Page, username: string) {
  await loginAs(page, username)
  const response = await page.request.post('/api/e2e/session', {
    data: { username },
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok()) {
    throw new Error(`e2e nextauth session failed: ${response.status()} ${await response.text()}`)
  }
}
