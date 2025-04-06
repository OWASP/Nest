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
    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])
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
    await expect(page.getByText('Leader 1').first()).toBeVisible()
    await expect(page.getByText('Mar 18, 2025').first()).toBeVisible()
    await page.getByRole('link', { name: 'Chapter 1' }).click()
    await expect(page).toHaveURL('chapters/chapter_1')
  })
  test('should have new projects', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'New Projects' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Project 1', exact: true })).toBeVisible()
    await expect(page.getByText('Leader 1,').first()).toBeVisible()
    await expect(page.getByText('Mar 5, 2025').first()).toBeVisible()
    await page.getByRole('link', { name: 'Project 1' }).click()
    await expect(page).toHaveURL('projects/project_1')
  })

  test('should have posts', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'News & Opinions' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Post 1', exact: true })).toBeVisible()
    await expect(page.getByText('Author 1')).toBeVisible()
    await expect(page.getByText('Mar 6, 2025').first()).toBeVisible({ timeout: 10000 })
    await page.getByRole('link', { name: 'Post 1' }).click()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Top Contributors' })).toBeVisible()
    await expect(page.getByRole('img', { name: 'Contributor 1' })).toBeVisible()
    await expect(page.getByText('Contributor 1')).toBeVisible()
    await expect(page.getByText('OWASP Juice Shop')).toBeVisible()
  })

  test('should have recent issues', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Issues' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Issue 1' })).toBeVisible()
    await expect(page.getByText('Mar 20, 2025').first()).toBeVisible()
    await expect(page.getByText('5 comments')).toBeVisible()
  })

  test('should have recent Releases', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Recent Releases' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Release 1' })).toBeVisible()
    await expect(page.getByText('Mar 19, 2025')).toBeVisible()
    await expect(page.getByText('repo-1')).toBeVisible()
  })

  test('should be able to join OWASP', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Ready to Make a Difference?' })).toBeVisible()
    await expect(page.getByText('Join OWASP and be part of the')).toBeVisible()
    await expect(page.getByRole('link', { name: 'Join OWASP', exact: true })).toBeVisible()
    const page1Promise = page.waitForEvent('popup')
    await page.getByRole('link', { name: 'Join OWASP', exact: true }).click()
    const page1 = await page1Promise
    expect(page1.url()).toBe('https://owasp.glueup.com/organization/6727/memberships/')
  })

  test('should have upcoming events', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Upcoming Events' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Event 1' })).toBeVisible()
    await expect(page.getByText('Apr 5 — 6, 2025')).toBeVisible()
    await page.getByRole('button', { name: 'Event 1' }).click()
  })
})
