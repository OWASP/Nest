import { test, expect } from '@playwright/test'

test.describe('Chapter Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/chapters/rosario', { timeout: 25000 })
    await page.waitForLoadState('domcontentloaded')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Rosario', exact: true })).toBeVisible()
    await expect(
      page.getByText(/The OWASP Rosario chapter is located in Argentina, South America/i)
    ).toBeVisible()
  })

  test('should have chapter details block', async ({ page }) => {
    await expect(page.getByText('Location: Rosario, Santa Fe, Argentina')).toBeVisible()
    await expect(page.getByText('Region: South America')).toBeVisible()
    await expect(
      page.getByRole('link', { name: 'https://owasp.org/www-chapter-rosario' })
    ).toBeVisible()
  })

  test('should have map with geolocation', async ({ page }) => {
    const unlockButton = page.getByRole('button', { name: 'Unlock map' })
    await expect(unlockButton).toBeVisible()

    // Use keyboard navigation to activate the button (bypasses pointer interception issues)
    await unlockButton.focus()
    await page.keyboard.press('Enter')

    // Wait for map to activate and controls to appear
    await page.waitForTimeout(500)

    await expect(page.getByRole('button', { name: 'Zoom in' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Zoom out' })).toBeVisible()

    const marker = page.locator('.leaflet-marker-icon').first()
    await marker.click()

    // The popup typically matches the chapter name
    const popupButton = page.getByRole('button', { name: 'OWASP Rosario' })
    await expect(popupButton).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(
      page.getByRole('img', { name: "Tomas Illuminati Balbin's avatar", exact: true })
    ).toBeVisible()
    await expect(page.getByText('Tomas Illuminati Balbin', { exact: true })).toBeVisible()
  })

  test('should have buttons for sponsoring', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Sponsor OWASP Rosario' })).toBeVisible()
  })
})
