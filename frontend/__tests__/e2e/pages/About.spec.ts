import { test, expect } from '@playwright/test'
import { mockAboutData } from '@unit/data/mockAboutData'

test.describe('About Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/idx/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          hits: [mockAboutData.project],
          nbPages: 1,
        }),
      })
    })

    await page.goto('/about')
  })

  test('renders main sections correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'About' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Project history' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Roadmap' })).toBeVisible()
  })

  test('displays leader information correctly', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Arkadii Yakovets Arkadii' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Kateryna Golovanova Kateryna' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Starr Brown Starr Brown OWASP' })).toBeVisible()
  })

  test('displays contributor information when data is loaded', async ({ page }) => {
    await expect(page.getByText('Contributor 1')).toBeVisible()
    await expect(page.getByText('Contributor 2')).toBeVisible()
  })

  test('loads roadmap items correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Roadmap' })).toBeVisible()
    expect(await page.locator('li').count()).toBeGreaterThan(0)
  })

  test('displays animated counters with correct values', async ({ page }) => {
    await expect(page.getByText('1.2K+Contributors')).toBeVisible()
    await expect(page.getByText('40+Issues')).toBeVisible()
    await expect(page.getByText('60+Forks')).toBeVisible()
    await expect(page.getByText('890+Stars')).toBeVisible()
  })

  test('opens GitHub profile in new window when leader button is clicked', async ({
    page,
    context,
  }) => {
    const pagePromise = context.waitForEvent('page')
    await page.getByRole('button', { name: 'View profile' }).first().click()
    const newPage = await pagePromise
    await newPage.waitForLoadState()
    expect(newPage.url()).toContain('github.com')
  })
})
