import { test, expect } from '@playwright/test'

test.describe('Footer Social Media Icons', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('Bluesky icon should be present and link correctly', async ({ page }) => {
    const blueskyIcon = page.locator('footer a[href="https://bsky.app/profile/nest.owasp.org"]')
    await expect(blueskyIcon).toBeVisible()
    await expect(blueskyIcon).toHaveAttribute('target', '_blank')
  })

  test('GitHub icon should be present and link correctly', async ({ page }) => {
    const githubIcon = page.locator('footer a[href="https://github.com/owasp/nest"]')
    await expect(githubIcon).toBeVisible()
    await expect(githubIcon).toHaveAttribute('target', '_blank')
  })

  test('Slack icon should be present and link correctly', async ({ page }) => {
    const slackIcon = page.locator('footer a[href="https://owasp.slack.com/archives/project-nest"]')
    await expect(slackIcon).toBeVisible()
    await expect(slackIcon).toHaveAttribute('target', '_blank')
  })
})
