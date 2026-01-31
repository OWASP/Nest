import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Home Page', () => {
  let context: BrowserContext
  let page: Page

  test.beforeAll(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      baseURL: testInfo.project.use.baseURL,
    })
    page = await context.newPage()
    await page.goto('/', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have a heading', async () => {
    await expect(page.getByRole('heading', { name: 'OWASP Nest', exact: true })).toBeVisible()
    await expect(
      page.getByText('Your gateway to OWASP. Discover, engage, and help shape the future!')
    ).toBeVisible()
  })

  test('should have new chapters', async () => {
    await expect(page.getByRole('heading', { name: 'New Chapters' })).toBeVisible()
    // Select the first chapter link in the "New Chapters" section
    const firstChapter = page
      .locator('div')
      .filter({ hasText: 'New Chapters' })
      .locator('a')
      .first()
    await expect(firstChapter).toBeVisible()
  })

  test('should have new projects', async () => {
    await expect(page.getByRole('heading', { name: 'New Projects' })).toBeVisible()
    const firstProject = page
      .locator('div')
      .filter({ hasText: 'New Projects' })
      .locator('a')
      .first()
    await expect(firstProject).toBeVisible()
  })

  test('should have top contributors', async () => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    // Look for the contributor grid/list
    const contributor = page.locator('img[alt*="avatar"]').first()
    await expect(contributor).toBeVisible()
  })

  test('should have recent activity sections', async () => {
    // These sections often load dynamically; grouping to ensure data exists
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()
  })

  test('should be able to join OWASP', async () => {
    await expect(page.getByRole('heading', { name: 'Ready to Make a Difference?' })).toBeVisible()
    const joinLink = page.getByRole('link', { name: 'Join OWASP', exact: true })
    await expect(joinLink).toBeVisible()
  })

  test('should have stats', async () => {
    const statLabels = ['Active Projects', 'Local Chapters', 'Contributors', 'Countries']
    for (const label of statLabels) {
      await expect(page.getByText(label, { exact: true })).toBeVisible()
    }
  })

  test('footer social icons should be present', async () => {
    const platforms = ['Bluesky', 'GitHub', 'Slack']
    for (const platform of platforms) {
      const icon = page.locator(`footer a[aria-label*="${platform}"]`)
      await expect(icon).toBeVisible()
      await expect(icon).toHaveAttribute('target', '_blank')
    }
  })
})
