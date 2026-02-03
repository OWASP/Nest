import { test, expect } from '@playwright/test'

test.describe('Organization Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/organizations/OWASP', { timeout: 25000 })
  })

  test('should have a heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP', exact: true })).toBeVisible()
  })

  test('should display organization details', async ({ page }) => {
    await expect(page.getByText('@OWASP')).toBeVisible()
    await expect(page.getByText('United States of America')).toBeVisible()
  })

  test('should display organization statistics', async ({ page }) => {
    const stats = ['Stars', 'Forks', 'Contributors', 'Issues', 'Repositories']
    for (const stat of stats) {
      await expect(page.getByText(stat).first()).toBeVisible()
      // Verify that there is a number associated with the stat (e.g., "15.4K Stars")
      const text = String.raw`\d.*${stat}`
      await expect(
        page
          .locator('div')
          .filter({ hasText: new RegExp(text) })
          .first()
      ).toBeVisible()
    }
  })

  test('should display recent issues section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    // Validate that at least one issue is listed
    const firstIssue = page.locator('div').filter({ hasText: 'Recent Issues' }).locator('a').first()
    await expect(firstIssue).toBeVisible()
  })

  test('should have organization recent milestones', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible({
      timeout: 10000,
    })
    const milestone = page
      .locator('div')
      .filter({ hasText: 'Recent Milestones' })
      .locator('h3')
      .first()
    await expect(milestone).toBeVisible()
  })

  test('should display recent releases section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    const releaseLink = page
      .locator('div')
      .filter({ hasText: 'Recent Releases' })
      .locator('a')
      .first()
    await expect(releaseLink).toBeVisible()
  })

  test('should display top contributors section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    const contributorAvatar = page.locator('img[alt*="avatar"]').first()
    await expect(contributorAvatar).toBeVisible()
  })

  test('should display recent pull requests section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    const firstPR = page
      .locator('div')
      .filter({ hasText: 'Recent Pull Requests' })
      .locator('a')
      .first()
    await expect(firstPR).toBeVisible()
  })
})
