import { test, expect, Page } from '@playwright/test'
import { mockCommitteeDetailsData } from '@unit/data/mockCommitteeDetailsData'

function getFirstHeading(page: Page, name: string) {
  return page.getByRole('heading', { name }).first()
}

test.describe('Committee Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockCommitteeDetailsData },
      })
    })
    await page.goto('/committees/test-committee')
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Committee' })).toBeVisible()
    await expect(page.getByText('This is a test committee')).toBeVisible()
  })

  test('should have committee details block', async ({ page }) => {
    await expect(getFirstHeading(page, 'Committee Details')).toBeVisible()
    await expect(page.getByText('Last Updated: Dec 13, 2024')).toBeVisible()
    await expect(page.getByText('Leaders: Leader 1, Leader 2')).toBeVisible()
    await expect(page.getByRole('link', { name: 'https://owasp.org/test-committee' })).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(getFirstHeading(page, 'Top Contributors')).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 1' })).toBeVisible()
    await expect(page.getByText('Contributor 1')).toBeVisible()
    await expect(page.getByText('2157 Contributions')).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 2' })).toBeVisible()
    await expect(page.getByText('Contributor 2')).toBeVisible()
    await expect(page.getByText('309 Contributions')).toBeVisible()
  })
})
