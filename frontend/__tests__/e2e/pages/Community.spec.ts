import { test, expect } from '@playwright/test'
import {
  exploreCards as NAV_SECTIONS,
  engagementWays,
  journeySteps,
} from '../../../src/utils/communityData'

test.describe('Community Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/community', { timeout: 25000 })
  })

  test('renders main heading', async ({ page }) => {
    await expect(
      page.getByRole('heading', { name: 'OWASP Community', level: 1 })
    ).toBeVisible()
  })

  test('renders hero description with navigation links', async ({ page }) => {
    const heroDesc = page.locator('p').filter({ hasText: 'Explore the vibrant OWASP community' })
    await expect(heroDesc.getByRole('link', { name: 'Chapters' })).toBeVisible()
    await expect(heroDesc.getByRole('link', { name: 'Members' })).toBeVisible()
    await expect(heroDesc.getByRole('link', { name: 'Organizations' })).toBeVisible()
  })

  test('renders Explore Resources section with all navigation cards', async ({ page }) => {
    await expect(page.getByText('Explore Resources')).toBeVisible()

    for (const { href, description } of NAV_SECTIONS) {
      const link = page.getByRole('link').filter({ hasText: description })
      await expect(link).toBeVisible()
      await expect(link).toHaveAttribute('href', href)
    }
  })

  test('renders Ways to Engage section with all engagement types', async ({ page }) => {
    await expect(page.getByText('Ways to Engage')).toBeVisible()

    for (const { title } of engagementWays) {
      await expect(page.getByText(title)).toBeVisible()
    }
  })

  test('renders Community Journey section with all steps', async ({ page }) => {
    for (const { label } of journeySteps) {
      await expect(
        page.getByRole('heading', { name: label, level: 3 }).first()
      ).toBeVisible()
    }
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
    await expect(
      page.getByRole('heading', { name: 'Ready to Get Involved?' })
    ).toBeVisible()

    const cta = page.getByRole('link', { name: 'contributing to a project' })
    await expect(cta).toBeVisible()
    await expect(cta).toHaveAttribute('href', '/contribute')
  })

  test('Snapshots explore card navigates correctly', async ({ page }) => {
    const snapshotsCard = page.getByRole('link', { name: 'Snapshots' }).first()
    await expect(snapshotsCard).toBeVisible()
    await expect(snapshotsCard).toHaveAttribute('href', '/community/snapshots')
  })
})