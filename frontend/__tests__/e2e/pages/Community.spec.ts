import { test, expect } from '@playwright/test'

test.describe('Community Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/community', { timeout: 25000 })
  })

  test('renders main heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Community', level: 1 })).toBeVisible()
  })

  test('renders hero description with navigation links', async ({ page }) => {
    const heroDesc = page.locator('p').filter({ hasText: 'Explore the vibrant OWASP community' })
    await expect(heroDesc.getByRole('link', { name: 'Chapters' })).toBeVisible()
    await expect(heroDesc.getByRole('link', { name: 'Members' })).toBeVisible()
    await expect(heroDesc.getByRole('link', { name: 'Organizations' })).toBeVisible()
  })

  test('renders Explore Resources with representative navigation cards', async ({ page }) => {
    await expect(page.getByText('Explore Resources')).toBeVisible()

    const chapters = page.getByRole('link').filter({ hasText: 'Find local OWASP chapters' })
    await expect(chapters).toBeVisible()
    await expect(chapters).toHaveAttribute('href', '/chapters')

    const snapshots = page.getByRole('link').filter({ hasText: 'View community snapshots' })
    await expect(snapshots).toBeVisible()
    await expect(snapshots).toHaveAttribute('href', '/community/snapshots')
  })

  test('renders Ways to Engage section', async ({ page }) => {
    await expect(page.getByText('Ways to Engage')).toBeVisible()
    await expect(page.getByText('Join Local Chapters')).toBeVisible()
    await expect(page.getByText('Contribute to Projects')).toBeVisible()
  })

  test('renders Community Journey section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Discover', level: 3 }).first()).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Contribute', level: 3 }).first()).toBeVisible()
  })

  test('renders Join Slack section with working link', async ({ page }) => {
    await expect(
      page.getByText('Connect with fellow security professionals', { exact: false })
    ).toBeVisible()

    const slackLink = page.getByRole('link', { name: 'Join OWASP Community Slack workspace' })
    await expect(slackLink).toBeVisible()
    await expect(slackLink).toHaveAttribute('href', 'https://owasp.org/slack/invite')
    await expect(slackLink).toHaveAttribute('target', '_blank')
    await expect(slackLink).toHaveAttribute('rel', 'noopener noreferrer')
  })

  test('renders Ready to Get Involved CTA section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Ready to Get Involved?' })).toBeVisible()

    const cta = page.getByRole('link', { name: 'contributing to a project' })
    await expect(cta).toBeVisible()
    await expect(cta).toHaveAttribute('href', '/contribute')
  })
})
