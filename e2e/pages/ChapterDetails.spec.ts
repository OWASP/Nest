import { test, expect } from '@playwright/test'

test.describe('Chapter Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/chapters/rosario', { timeout: 25000 })
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
    await unlockButton.waitFor({ state: 'attached', timeout: 30000 })

    await unlockButton.dispatchEvent('click')

    await unlockButton.waitFor({ state: 'detached', timeout: 10000 })

    await page.locator('.leaflet-control-zoom-in').waitFor({ state: 'attached', timeout: 10000 })
    await page.locator('.leaflet-control-zoom-out').waitFor({ state: 'attached', timeout: 10000 })

    await page.locator('.leaflet-container').waitFor({ state: 'attached' })
    await page.locator('.leaflet-tile-pane').waitFor({ state: 'attached' })
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
