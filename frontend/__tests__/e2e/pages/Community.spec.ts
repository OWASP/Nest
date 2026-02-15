import { mockCommunityData } from '@e2e/data/mockCommunityData'
import { mockHomeData } from '@e2e/data/mockHomeData'
import { test, expect } from '@playwright/test'

test.describe('Community Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      const combinedData = {
        data: {
          ...mockHomeData.data,
          ...mockCommunityData.data,
        },
      }
      await route.fulfill({
        status: 200,
        json: combinedData,
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
    await page.goto('/community')
  })

  test('should have a heading and intro text', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Community' })).toBeVisible()
    await expect(
      page.getByText(
        "Connect, collaborate, and contribute to the world's largest application security community."
      )
    ).toBeVisible()
    await expect(page.getByPlaceholder('Search the OWASP community')).toBeVisible()
  })

  test('should have navigation cards', async ({ page }) => {
    const navSection = page.locator('.grid.grid-cols-2').first()
    await expect(navSection.getByRole('link', { name: 'Chapters' })).toBeVisible()
    await expect(navSection.getByRole('link', { name: 'Members' })).toBeVisible()
    await expect(navSection.getByRole('link', { name: 'Organizations' })).toBeVisible()
  })

  test('should have new chapters', async ({ page }) => {
    await expect(page.getByText('New Chapters', { exact: true })).toBeVisible()
    await expect(page.getByText('Chapter 1')).toBeVisible()
    await expect(page.getByText('Pune, Maharashtra, India')).toBeVisible()
  })

  test('should have new organizations', async ({ page }) => {
    await expect(page.getByText('New Organizations', { exact: true })).toBeVisible()
    await expect(page.getByText('Organization 1')).toBeVisible()
  })

  test('should have snapshots', async ({ page }) => {
    await expect(page.getByText('Snapshot 1')).toBeVisible()
    await expect(page.getByText('Jan 1, 2025 - Jan 31, 2025')).toBeVisible()
  })

  test('should have top contributors', async ({ page }) => {
    await expect(page.getByText('Top Contributors', { exact: true })).toBeVisible()
    await expect(page.getByText('Contributor 1')).toBeVisible()
  })

  test('should have stats', async ({ page }) => {
    await expect(page.getByText('Active Chapters')).toBeVisible()
    await expect(page.getByText('150+', { exact: true })).toBeVisible()
    await expect(page.getByText('Active Projects')).toBeVisible()
    await expect(page.getByText('50+', { exact: true })).toBeVisible()
    await expect(page.getByText(/5k\+/i)).toBeVisible()
  })
})
