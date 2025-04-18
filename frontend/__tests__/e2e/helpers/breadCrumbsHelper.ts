import { Page, expect } from '@playwright/test'

export async function expectBreadcrumbVisible(page: Page, items: string[] = ['Home']) {
  const breadcrumb = page.locator('[aria-label="breadcrumb"]')
  await expect(breadcrumb).toBeVisible()
  for (const item of items) {
    await expect(breadcrumb.getByText(item)).toBeVisible()
  }
}
