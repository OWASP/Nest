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
