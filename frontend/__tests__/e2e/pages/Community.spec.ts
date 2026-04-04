import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { test, expect } from '@playwright/test'

test.describe('Community Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/community', { timeout: 25000 })
  })

  test('renders main heading and description', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Community' })).toBeVisible()
    await expect(
      page.getByText('Explore the vibrant OWASP community', { exact: false })
    ).toBeVisible()
  })

  test('renders explore resources section', async ({ page }) => {
    await expect(page.getByText('Explore Resources')).toBeVisible()
    await expect(page.getByRole('link', { name: /Chapters/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Members/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Organizations/i })).toBeVisible()
  })

  test('renders ways to engage section', async ({ page }) => {
    await expect(page.getByText('Ways to Engage')).toBeVisible()
  })

  test('renders join slack section', async ({ page }) => {
    const joinSlackLink = page.getByRole('link', { name: 'Join Slack' })
    await expect(joinSlackLink).toBeVisible()
    await expect(joinSlackLink).toHaveAttribute('href', 'https://owasp.org/slack/invite')
    await expect(joinSlackLink).toHaveAttribute('target', '_blank')
  })

  test('renders call to action section', async ({ page }) => {
    await expect(
      page.getByRole('heading', { name: 'Ready to Get Involved?' })
    ).toBeVisible()
    await expect(page.getByRole('link', { name: 'contributing to a project' })).toBeVisible()
  })

  test('breadcrumb renders correct segments on /community', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Community'])
  })
})
