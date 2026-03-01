import { mockChapterDetailsData } from '@mockData/mockChapterDetailsData'
import { test, expect } from '@playwright/test'

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

  test('should have Slack channel link', async ({ page }) => {
    const slackLink = page.getByRole('link', { name: 'chapter-test' })
    await expect(slackLink).toBeVisible()
    await expect(slackLink).toHaveAttribute('href', 'https://owasp.slack.com/archives/C123ABC')
    await expect(slackLink).toHaveAttribute('target', '_blank')
  })

  test('should have map with geolocation', async ({ page }) => {
    const unlockButton = page.getByRole('button', { name: 'Unlock map' })
    await expect(unlockButton).toBeVisible()

    await unlockButton.click()

    await expect(page.getByRole('button', { name: 'Zoom in' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Zoom out' })).toBeVisible()

    const marker = page.locator('.leaflet-marker-icon').first()
    await marker.click()

    const popupButton = page.getByRole('button', { name: 'OWASP Test Chapter' })
    await expect(popupButton).toBeVisible()
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
