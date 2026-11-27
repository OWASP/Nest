import { Locator, Page, expect } from '@playwright/test'

export async function expectBreadCrumbsToBeVisible(page: Page, breadcrumbs: string[] = ['Home']) {
  const breadcrumbsContainer = page.locator('[aria-label="breadcrumb"]')

  await expect(breadcrumbsContainer).toBeVisible()
  await expect(breadcrumbsContainer).toHaveCount(1)

  for (const breadcrumb of breadcrumbs) {
    await expect(breadcrumbsContainer.getByText(breadcrumb)).toBeVisible()
  }

  const allBreadcrumbs = await breadcrumbsContainer.locator('li').allTextContents()
  const visibleBreadcrumbs = allBreadcrumbs.filter((text) => text.trim() !== '')
  expect(visibleBreadcrumbs).toEqual(breadcrumbs)
}

// Returns the rendered gap in px between the page search input and the element directly below it.
export async function getGapBelowSearch(page: Page, below: Locator): Promise<number> {
  const search = page.getByPlaceholder(/^Search for/)

  await expect(search).toBeVisible()
  await expect(below).toBeVisible()

  const searchBox = await search.boundingBox()
  const belowBox = await below.boundingBox()
  if (!searchBox || !belowBox) {
    throw new Error('Search input or the element below it has no layout box')
  }

  return Math.round(belowBox.y - (searchBox.y + searchBox.height))
}
