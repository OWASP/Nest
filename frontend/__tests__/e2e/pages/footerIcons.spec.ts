import { test, expect } from '@playwright/test'

test.describe('Footer Social Media Icons', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('Bluesky icon should be present and link correctly', async ({ page }) => {
    const blueskyIcon = page.locator('footer a[aria-label="OWASP Nest Bluesky"]')
    await expect(blueskyIcon).toBeVisible()
    await expect(blueskyIcon).toHaveAttribute('target', '_blank')
  })

  test('GitHub icon should be present and link correctly', async ({ page }) => {
    const githubIcon = page.locator('footer a[aria-label="OWASP Nest GitHub"]')
    await expect(githubIcon).toBeVisible()
    await expect(githubIcon).toHaveAttribute('target', '_blank')
  })

  test('Slack icon should be present and link correctly', async ({ page }) => {
    const slackIcon = page.locator('footer a[aria-label="OWASP Nest Slack"]')
    await expect(slackIcon).toBeVisible()
    await expect(slackIcon).toHaveAttribute('target', '_blank')
  })
})
