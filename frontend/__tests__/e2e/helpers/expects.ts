import { Page, expect } from '@playwright/test'

export async function expectBreadCrumbsToBeVisible(page: Page, breadcrumbs: string[] = ['Home']) {
  const breadcrumbsContainer = page.locator('[aria-label="breadcrumb"]')

  await expect(breadcrumbsContainer).toBeVisible()
  await expect(breadcrumbsContainer).toHaveCount(1)

  for (const breadcrumb of breadcrumbs) {
    await expect(breadcrumbsContainer.getByText(breadcrumb)).toBeVisible()
  }
}
