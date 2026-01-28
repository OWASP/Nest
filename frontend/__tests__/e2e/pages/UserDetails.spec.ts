import { test, expect, Page, BrowserContext } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

test.describe('User Details Page', () => {
  let context: BrowserContext
  let page: Page

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/members/arkid15r', { timeout: 25000 })
  })

  test.afterAll(async () => {
    await context.close()
  })

  test('should have a heading and summary', async () => {
    await expect(page.getByRole('heading', { name: 'Arkadii Yakovets', exact: true })).toBeVisible()
    await expect(page.getByText('@arkid15r')).toBeVisible()
  })

  test('should have user details block', async () => {
    await expect(page.getByRole('heading', { name: 'User Details' })).toBeVisible()
    await expect(page.getByText(/Location:/i)).toBeVisible()
    await expect(page.getByText(/Email:/i)).toBeVisible()
    await expect(page.getByRole('link', { name: 'github.com/arkid15r' })).toBeVisible()
  })

  test('should have user stats block', async () => {
    // Validation of stats grid using regex to handle changing numbers
    const stats = ['Followers', 'Following', 'Repositories']
    for (const stat of stats) {
      await expect(
        page
          .locator('div')
          .filter({ hasText: new RegExp(`\\d.*${stat}`) })
          .first()
      ).toBeVisible()
    }
  })

  test('should have user activity sections', async () => {
    // Check for standard activity headings
    await expect(page.getByRole('heading', { name: 'Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Pull Requests' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Repositories' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Recent Milestones' })).toBeVisible()
    // Verify that at least one repository is listed in the repos section
    const firstRepo = page
      .locator('section')
      .filter({ hasText: 'Repositories' })
      .locator('a')
      .first()
    await expect(firstRepo).toBeVisible()
  })
})
