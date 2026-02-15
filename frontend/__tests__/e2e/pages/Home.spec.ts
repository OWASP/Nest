import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { timeout: 25000 })
  })

  test('should have a heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Nest', exact: true })).toBeVisible()
    await expect(
      page.getByText('Your gateway to OWASP. Discover, engage, and help shape the future!')
    ).toBeVisible()
  })

  test('should have new chapters', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'New Chapters' })).toBeVisible()
    // Select the first chapter link in the "New Chapters" section
    const firstChapter = page
      .locator('div')
      .filter({ hasText: 'New Chapters' })
      .locator('a')
      .first()
    await expect(firstChapter).toBeVisible()
  })

  test('should have new projects', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'New Projects' })).toBeVisible()
    const firstProject = page
      .locator('div')
      .filter({ hasText: 'New Projects' })
      .locator('a')
      .first()
    await expect(firstProject).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    // Look for the contributor grid/list
    const contributor = page.locator('img[alt*="avatar"]').first()
    await expect(contributor).toBeVisible()
  })

  test('should have recent activity sections', async ({ page }) => {
    // These sections often load dynamically; grouping to ensure data exists (using data-anchor-title attribute for AnchorTitle components)
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Issues' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Releases' })
    ).toBeVisible()
    await expect(
      page.locator('[data-anchor-title="true"]', { hasText: 'Recent Milestones' })
    ).toBeVisible()
  })

  test('should be able to join OWASP', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Ready to Make a Difference?' })).toBeVisible()
    const joinLink = page.getByRole('link', { name: 'Join OWASP', exact: true })
    await expect(joinLink).toBeVisible()
  })

  test('should have stats', async ({ page }) => {
    const statLabels = ['Active Projects', 'Local Chapters', 'Contributors', 'Countries']
    for (const label of statLabels) {
      await expect(page.getByText(label, { exact: true })).toBeVisible()
    }
  })

  test('footer social icons should be present', async ({ page }) => {
    const platforms = ['Bluesky', 'GitHub', 'Slack']
    for (const platform of platforms) {
      const icon = page.locator(`footer a[aria-label*="${platform}"]`)
      await expect(icon).toBeVisible()
      await expect(icon).toHaveAttribute('target', '_blank')
    }
  })
})
