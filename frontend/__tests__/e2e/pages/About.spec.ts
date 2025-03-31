import { test, expect } from '@playwright/test'
import { mockAboutData } from '@unit/data/mockAboutData'

test.describe('About Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      const request = route.request()
      const postData = request.postDataJSON()

      if (postData.query?.includes('user')) {
        const username = postData.variables.key
        const userData = mockAboutData.users[username]
        await route.fulfill({ status: 200, json: { data: { user: userData } } })
      } else {
        await route.fulfill({ status: 200, json: { data: { project: mockAboutData.project } } })
      }
    })

    await page.goto('/about')
  })

  test('renders main sections correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'About' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'History' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Roadmap' })).toBeVisible()
  })

  test('displays contributor information when data is loaded', async ({ page }) => {
    await expect(page.getByText('Contributor 1')).toBeVisible()
    await expect(page.getByText('Contributor 2')).toBeVisible()
  })

  test('displays leaders data when data is loaded', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
  })

  test('displays technologies & Tools', async ({ page }) => {
    const technologies = [
      'Ansible',
      'Docker',
      'Jest',
      'PlayWright',
      'PostgreSQL',
      'Pytest',
      'React',
      'Tailwind CSS',
      'Typescript',
    ]

    for (const tech of technologies) {
      await expect(page.getByText(tech)).toBeVisible()
    }
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

  test('opens user profile in new window when leader button is clicked', async ({
    page,
    context,
  }) => {
    const pagePromise = context.waitForEvent('page')
    await page.getByRole('button', { name: 'View Profile' }).first().click()
    const newPage = await pagePromise
    await newPage.waitForLoadState()
    expect(newPage.url()).toContain('/community/users/')
  })
})
