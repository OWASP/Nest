import { test, expect } from '@playwright/test'
import { mockChapterDetailsData } from '@unit/data/mockChapterDetailsData'

test.describe('Chapter Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: { data: { chapter: mockChapterDetailsData } },
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
})
