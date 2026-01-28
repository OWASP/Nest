import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Repository Details Page', () => {
  let context: BrowserContext
  let page: Page

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/organizations/OWASP/repositories/Nest', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have a heading and summary', async () => {
    await expect(page.getByRole('heading', { name: 'Nest', exact: true })).toBeVisible()
    await expect(page.getByText(/OWASP Nest is a platform/i)).toBeVisible()
  })

  test('should have repository details block', async () => {
    await expect(page.getByRole('heading', { name: 'Repository Details' })).toBeVisible()

    // License is Apache-2.0 for Nest
    await expect(page.getByText(/License:.*Apache-2\.0/i)).toBeVisible()

    // Check that there is a link to the GitHub repo
    await expect(page.getByRole('link', { name: 'https://github.com/OWASP/Nest' })).toBeVisible()

    // Verify "Last Updated" text is present (date will vary)
    await expect(page.getByText(/Last Updated:/i)).toBeVisible()
  })

  test('should have statistics block', async () => {
    const stats = ['Stars', 'Forks', 'Contributors', 'Issues', 'Commits']
    for (const stat of stats) {
      // Look for the stat label and ensure a number is nearby
      await expect(
        page
          .locator('div')
          .filter({ hasText: new RegExp(`\\d.*${stat}`) })
          .first()
      ).toBeVisible()
    }
  })

  test('should have topics', async () => {
    await expect(page.getByRole('heading', { name: 'Topics' })).toBeVisible()
    const topics = ['python', 'nextjs', 'typescript']
    for (const topic of topics) {
      await expect(page.getByText(topic)).toBeVisible()
    }
  })

  test('should have languages', async () => {
    await expect(page.getByRole('heading', { name: 'Languages' })).toBeVisible()
    await expect(page.getByText('TypeScript', { exact: true })).toBeVisible()
    await expect(page.getByText('Python', { exact: true })).toBeVisible()
  })

  test('should have top contributors', async () => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    // Check for presence of contributor avatars/names
    const contributor = page.locator('img[alt*="avatar"]').first()
    await expect(contributor).toBeVisible()
  })

  test('toggle top contributors', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
    await page.getByRole('button', { name: 'Show more' }).click()
    await expect(page.getByRole('button', { name: 'Show less' })).toBeVisible()
    await page.getByRole('button', { name: 'Show less' }).click()
    await expect(page.getByRole('button', { name: 'Show more' })).toBeVisible()
  })

  test('should have recent activity sections', async () => {
    // Grouping activity checks as they are dynamic lists
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()

    // Verify that at least one item exists in the PR section
    const firstPR = page
      .locator('section')
      .filter({ hasText: 'Recent Pull Requests' })
      .locator('a')
      .first()
    await expect(firstPR).toBeVisible()
  })
})
