import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
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
      } else if (postData.query?.includes('topContributors')) {
        await route.fulfill({
          status: 200,
          json: { data: { topContributors: mockAboutData.topContributors } },
        })
      } else {
        await route.fulfill({ status: 200, json: { data: { project: mockAboutData.project } } })
      }
    })

    await page.context().addCookies([
      {
        name: 'csrftoken',
        value: 'abc123',
        domain: 'localhost',
        path: '/',
      },
    ])

    await page.goto('/about')
  })

  test('renders main sections correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'About' })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Project Timeline/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Our Story/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Roadmap/ })).toBeVisible()
  })

  test('displays contributor information when data is loaded', async ({ page }) => {
    await expect(page.getByText('Contributor 1', { exact: true })).toBeVisible()
    await expect(page.getByText('Contributor 2', { exact: true })).toBeVisible()
  })

  test('displays leaders data when data is loaded', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
  })

  test('displays technologies & Tools', async ({ page }) => {
    const technologies = [
      'Ansible',
      'Docker',
      'Jest',
      'Next.js',
      'PlayWright',
      'PostgreSQL',
      'Pytest',
      'Tailwind CSS',
      'Typescript',
    ]

    for (const tech of technologies) {
      await expect(page.getByRole('link', { name: tech })).toBeVisible()
    }
  })

  test('loads roadmap items correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Roadmap/ })).toBeVisible()
    for (const milestone of mockAboutData.project.recentMilestones) {
      await expect(page.getByText(milestone.title)).toBeVisible()
      await expect(page.getByText(milestone.body)).toBeVisible()
    }
  })

  test('displays animated counters with correct values', async ({ page }) => {
    await expect(page.getByText('1.2K+Contributors')).toBeVisible()
    await expect(page.getByText('40+Open Issues')).toBeVisible()
    await expect(page.getByText('60+Forks')).toBeVisible()
    await expect(page.getByText('890+Stars')).toBeVisible()
  })

  test('opens user profile in new window when leader button is clicked', async ({ page }) => {
    await page.getByRole('button', { name: 'View Profile' }).first().click()
    await expect(page).toHaveURL('/members/arkid15r')
  })

  test('breadcrumb renders correct segments on /about', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'About'])
  })

  test('renders key features section', async ({ page }) => {
    await expect(page.getByText('Key Features')).toBeVisible()
    await expect(page.getByText('Advanced Community Search')).toBeVisible()
  })

  test('renders project history timeline section', async ({ page }) => {
    await expect(page.getByText('Project Timeline')).toBeVisible()
    await expect(page.getByText('Project Inception')).toBeVisible()
  })
})
