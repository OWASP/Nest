import { mockCommitteeDetailsData } from '@mockData/mockCommitteeDetailsData'
import { test, expect } from '@playwright/test'

test.describe('Committee Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockCommitteeDetailsData },
      })
    })
    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])
    await page.goto('/committees/test-committee')
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Test Committee' })).toBeVisible()
    await expect(page.getByText('This is a test committee')).toBeVisible()
  })

  test('should have committee details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Committee Details' })).toBeVisible()
    await expect(page.getByText('Last Updated: Dec 13, 2024')).toBeVisible()
    await expect(page.getByText('Leaders: Leader 1, Leader 2')).toBeVisible()
    await expect(page.getByRole('link', { name: 'https://owasp.org/test-committee' })).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 1' })).toBeVisible()
    await expect(page.getByText('Contributor 1')).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 2' })).toBeVisible()
    await expect(page.getByText('Contributor 2')).toBeVisible()
  })
})
