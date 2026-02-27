import { test, expect } from '@playwright/test'

test.describe('Committee Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/committees/events', { timeout: 25000 })
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(
      page.getByRole('heading', { name: 'OWASP Events Committee', exact: true })
    ).toBeVisible()
    await expect(
      page.getByText(
        'The OWASP Events Committee aims to support and enhance global, regional, and local events'
      )
    ).toBeVisible()
  })

  test('should have committee details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Committee Details' })).toBeVisible()

    // Verification of leaders (checking for presence of key names)
    const leadersText = page.getByText(/Leaders:.*Izar Tarandach, Allison Shubert, Maria Mora/i)
    await expect(leadersText).toBeVisible()

    await expect(
      page.getByRole('link', { name: 'https://owasp.org/www-committee-events' })
    ).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()

    await expect(page.getByRole('img', { name: "Josh Grossman's avatar" })).toBeVisible()
    await expect(page.getByText('Josh Grossman')).toBeVisible()

    await expect(page.getByRole('img', { name: "Harold Blankenship's avatar" })).toBeVisible()
    await expect(page.getByText('Harold Blankenship', { exact: true }).first()).toBeVisible()

    await expect(page.getByRole('img', { name: "Andrew van der Stock's avatar" })).toBeVisible()
    await expect(page.getByText('Andrew van der Stock')).toBeVisible()
  })
})
