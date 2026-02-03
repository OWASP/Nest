import { test, expect } from '@playwright/test'

test.describe('Repository Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/organizations/OWASP/repositories/Nest', { timeout: 25000 })
  })

  test('should have a heading and summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Nest', exact: true })).toBeVisible()
    await expect(page.getByText(/Your gateway to OWASP/i)).toBeVisible()
  })

  test('should have repository details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Repository Details' })).toBeVisible()

    await expect(page.getByText('License: MIT')).toBeVisible()

    // Check that there is a link to the GitHub repo
    await expect(page.getByRole('link', { name: 'https://github.com/OWASP/Nest' })).toBeVisible()

    // Verify "Last Updated" text is present (date will vary)
    await expect(page.getByText(/Last Updated:/i)).toBeVisible()
  })

  test('should have statistics block', async ({ page }) => {
    const stats = ['Stars', 'Forks', 'Contributors', 'Issues', 'Commits']
    for (const stat of stats) {
      // Look for the stat label and ensure a number is nearby
      const text = String.raw`\d.*${stat}`
      await expect(
        page
          .locator('div')
          .filter({ hasText: new RegExp(text) })
          .first()
      ).toBeVisible()
    }
  })

  test('should have topics', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Topics' })).toBeVisible()
    const topics = ['python', 'nextjs', 'typescript']
    for (const topic of topics) {
      await expect(page.getByText(topic).first()).toBeVisible()
    }
  })

  test('should have languages', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Languages' })).toBeVisible()
    await expect(page.getByText('TypeScript', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Python', { exact: true }).first()).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    // Check for presence of contributor avatars/names
    const contributor = page.locator('img[alt*="avatar"]').first()
    await expect(contributor).toBeVisible()
  })

  test('toggle top contributors', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Show more' }).last()).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).last().click()
    await expect(page.getByRole('button', { name: 'Show less' }).last()).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).last().click()
    await expect(page.getByRole('button', { name: 'Show more' }).last()).toBeVisible()
  })

  test('should have recent activity sections', async ({ page }) => {
    // Grouping activity checks as they are dynamic lists
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()
  })
})
