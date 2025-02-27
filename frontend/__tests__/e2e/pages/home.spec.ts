import { mockHomeData } from '@e2e/data/mockHomeData'
import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        json: mockHomeData,
      })
    })
    await page.goto('/')
  })

  test('should have a heading and searchBar', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Welcome to OWASP Nest' })).toBeVisible()
    await expect(
      page.getByText('Your gateway to OWASP. Discover, engage, and help shape the future!')
    ).toBeVisible()
    await expect(page.getByRole('textbox', { name: 'Search the OWASP community' })).toBeVisible()
    await page.getByRole('textbox', { name: 'Search the OWASP community' }).fill('owasp')
  })

  test('should have new chapters', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'New Chapters' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'chapter 1' })).toBeVisible()
    await expect(page.getByText('Feb 20,').first()).toBeVisible()
    await page.getByRole('link', { name: 'chapter 1' }).click()
    expect(page.url()).toContain('chapters/chapter-1')
  })
  test('should have new projects', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'New Projects' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Project 1' })).toBeVisible()
    await expect(page.getByText('Jan 1,').first()).toBeVisible()
    await page.getByRole('link', { name: 'Project 1' }).click()
    expect(page.url()).toContain('projects/project-1')
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 1' })).toBeVisible()
    await expect(page.getByText('Repository 1')).toBeVisible()
    await page.getByText('Contributor 1').click()
    expect(page.url()).toContain('community/users/contributor1')
  })

  test('should have recent issues', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Issue 1' })).toBeVisible()
    await expect(page.getByText('Author 1').first()).toBeVisible()
    await expect(page.getByText('Feb 24,').first()).toBeVisible()
    await expect(page.getByText('5 comments')).toBeVisible()
  })

  test('should have recent Releases', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Release 1' })).toBeVisible()
    await expect(page.getByText('Feb 22,')).toBeVisible()
    await expect(page.getByText('v1', { exact: true })).toBeVisible()
  })

  test('should be able to join OWASP', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Ready to Make a Difference?' })).toBeVisible()
    await expect(page.getByText('Join OWASP and be part of the')).toBeVisible()
    await expect(page.getByRole('link', { name: 'Join OWASP Now' })).toBeVisible()
    const page1Promise = page.waitForEvent('popup')
    await page.getByRole('link', { name: 'Join OWASP Now' }).click()
    const page1 = await page1Promise
    expect(page1.url()).toBe('https://owasp.glueup.com/organization/6727/memberships/')
  })
})
