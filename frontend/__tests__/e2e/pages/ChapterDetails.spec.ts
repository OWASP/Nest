import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe('Chapter Details Page', () => {
  let context: BrowserContext
  let page: Page

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/chapters/rosario', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have a heading and summary', async () => {
    await expect(page.getByRole('heading', { name: 'OWASP Rosario', exact: true })).toBeVisible()
    await expect(
      page.getByText(/The OWASP Rosario chapter is located in Argentina, South America/i)
    ).toBeVisible()
  })

  test('should have chapter details block', async () => {
    await expect(page.getByText('Location: Unknown')).toBeVisible()
    await expect(page.getByText('Region: South America')).toBeVisible()
    await expect(
      page.getByRole('link', { name: 'https://owasp.org/www-chapter-rosario' })
    ).toBeVisible()
  })

  test('should have map with geolocation', async () => {
    const unlockButton = page.getByRole('button', { name: 'Click to interact with map' })
    await expect(unlockButton).toBeVisible()

    await unlockButton.click()

    await expect(page.getByRole('button', { name: 'Zoom in' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Zoom out' })).toBeVisible()

    const marker = page.locator('.leaflet-marker-icon').first()
    await marker.click()

    // The popup typically matches the chapter name
    const popupButton = page.getByRole('button', { name: 'OWASP Rosario' })
    await expect(popupButton).toBeVisible()
  })

  test('should have top contributors', async () => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Tomas Illuminati Balbin's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Tomas Illuminati Balbin', { exact: true })).toBeVisible()
  })

  test('should have buttons for sponsoring', async () => {
    await expect(page.getByRole('link', { name: 'Sponsor OWASP Rosario' })).toBeVisible()
  })
})
