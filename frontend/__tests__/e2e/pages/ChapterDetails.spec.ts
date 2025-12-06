import { test, expect } from '@playwright/test'
import { mockChapterDetailsData } from '@unit/data/mockChapterDetailsData'

test.describe('Chapter Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: mockChapterDetailsData },
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
    await page.goto('/chapters/test-chapter')
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Test Chapter' })).toBeVisible()
    await expect(page.getByText('This is a test chapter summary.')).toBeVisible()
  })

  test('should have chapter details block', async ({ page }) => {
    await expect(page.getByText('Location: Test City, Test')).toBeVisible()
    await expect(page.getByText('Region: Test Region')).toBeVisible()
    await expect(page.getByRole('link', { name: 'https://owasp.org/test-chapter' })).toBeVisible()
  })

  test('should have map with geolocation', async ({ page }) => {
    await expect(page.locator('#chapter-map')).toBeVisible()
    await expect(page.locator('#chapter-map').locator('img').nth(1)).toBeVisible()

    await expect(page.getByRole('button', { name: 'Zoom in' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Zoom out' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Marker' })).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Contributor 1's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Contributor 1', { exact: true })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Contributor 2's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Contributor 2', { exact: true })).toBeVisible()
  })

  test('toggle top contributors', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).click()
    await expect(page.getByRole('button', { name: 'Show less' })).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).click()
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
  })

  test('should have leaders block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
    await expect(page.getByText('Bob')).toBeVisible()
    await expect(page.getByText('Chapter Leader')).toBeVisible()
  })
})
