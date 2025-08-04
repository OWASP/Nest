import { Page, expect } from '@playwright/test'

export async function expectBreadCrumbsToBeVisible(page: Page, breadcrumbs: string[] = ['Home']) {
  const breadcrumbsContainer = page.locator('nav[role="navigation"][aria-label="breadcrumb"]')

  await expect(breadcrumbsContainer).toBeVisible({ timeout: 10000 })
  await expect(breadcrumbsContainer).toHaveCount(1)

  const expectedBreadcrumbs = breadcrumbs[0] === 'Home' ? breadcrumbs : ['Home', ...breadcrumbs]

  for (const breadcrumb of expectedBreadcrumbs) {
    await expect(breadcrumbsContainer.getByText(breadcrumb, { exact: true })).toBeVisible({
      timeout: 5000,
    })
  }
}
