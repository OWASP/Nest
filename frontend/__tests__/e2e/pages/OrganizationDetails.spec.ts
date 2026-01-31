import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.serial('Organization Details Page', () => {
  let context: BrowserContext
  let page: Page

  test.beforeAll(async ({ browser }, testInfo) => {
    context = await browser.newContext({
      baseURL: testInfo.project.use.baseURL,
    })
    page = await context.newPage()
    await page.goto('/organizations/OWASP', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have a heading and summary', async () => {
    await expect(page.getByRole('heading', { name: 'OWASP', exact: true })).toBeVisible()
    await expect(page.getByText(/The Open Worldwide Application Security Project/i)).toBeVisible()
  })

  test('should display organization details', async () => {
    await expect(page.getByText('@OWASP')).toBeVisible()
    // OWASP Headquarters is in Bel Air, MD
    await expect(page.getByText('Bel Air, MD')).toBeVisible()
  })

  test('should display organization statistics', async () => {
    const stats = ['Stars', 'Forks', 'Contributors', 'Issues', 'Repositories']
    for (const stat of stats) {
      await expect(page.getByText(stat)).toBeVisible()
      // Verify that there is a number associated with the stat (e.g., "15.4K Stars")
      await expect(
        page
          .locator('div')
          .filter({ hasText: new RegExp(`\\d.*${stat}`) })
          .first()
      ).toBeVisible()
    }
  })

  test('should display recent issues section', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    // Validate that at least one issue is listed
    const firstIssue = page
      .locator('section')
      .filter({ hasText: 'Recent Issues' })
      .locator('a')
      .first()
    await expect(firstIssue).toBeVisible()
  })

  test('should have organization recent milestones', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible({
      timeout: 10000,
    })
    const milestone = page
      .locator('section')
      .filter({ hasText: 'Recent Milestones' })
      .locator('h3')
      .first()
    await expect(milestone).toBeVisible()
  })

  test('should display recent releases section', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    const releaseLink = page
      .locator('section')
      .filter({ hasText: 'Recent Releases' })
      .locator('a')
      .first()
    await expect(releaseLink).toBeVisible()
  })

  test('should display top contributors section', async () => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    const contributorAvatar = page.locator('img[alt*="avatar"]').first()
    await expect(contributorAvatar).toBeVisible()
  })

  test('should display recent pull requests section', async () => {
    await expect(page.getByRole('heading', { name: 'Recent Pull Requests' })).toBeVisible()
    const firstPR = page
      .locator('section')
      .filter({ hasText: 'Recent Pull Requests' })
      .locator('a')
      .first()
    await expect(firstPR).toBeVisible()
  })
})
