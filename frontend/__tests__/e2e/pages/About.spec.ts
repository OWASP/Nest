import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { test, expect, Page } from '@playwright/test'

test.describe.serial('About Page', () => {
  let page: Page
  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext()
    page = await context.newPage()
    await page.goto('/about', { timeout: 25000 })
  })
  test.afterAll(async () => {
    await page.close()
  })

  test('renders main sections correctly', async () => {
    await expect(page.getByRole('heading', { name: 'About' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Project Timeline' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Our Story' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Roadmap' })).toBeVisible()
  })

  test('displays contributor information when data is loaded', async () => {
    await expect(page.getByText('Ahmed Gouda', { exact: true })).toBeVisible()
    await expect(page.getByText('Abhay Mishra', { exact: true })).toBeVisible()
    await expect(page.getByText('Raj gupta', { exact: true })).toBeVisible()
  })

  test('displays leaders data when data is loaded', async () => {
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
  })

  test('displays technologies & Tools', async () => {
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

  test('loads roadmap items correctly', async () => {
    await expect(page.getByRole('heading', { name: 'Roadmap' })).toBeVisible()

    await expect(
      page.getByText('OWASP Board Activity Standardization and Data Programmatic Access')
    ).toBeVisible()
    await expect(
      page.getByText(
        'This milestone focuses on standardizing how OWASP Board activities are recorded, structured, and published, and on making this information available in structured formats designed for verification, analysis, and automation, as well as programmatically accessible formats via APIs and schemas. The objective is to create a consistent, auditable, and extensible representation of board actions -- including motions, votes, discussions, and decisions so they can be reliably accessed by tools, dashboards, and community members. This milestone reinforces OWASP’s commitment to openness, integrity, and community trust by making board-related information more transparent, auditable, and reliable.'
      )
    ).toBeVisible()

    const roadmapSection = page
      .locator('div')
      .filter({ has: page.getByRole('heading', { name: 'Roadmap' }) })
      .filter({ has: page.getByRole('button', { name: 'Show more' }) })
      .last()

    await roadmapSection.getByRole('button', { name: 'Show more' }).click()
  })

  test('displays project statistics', async () => {
    await expect(page.getByText('Contributors').last()).toBeVisible()
    await expect(page.getByText('Open Issues').last()).toBeVisible()
    await expect(page.getByText('Forks').last()).toBeVisible()
    await expect(page.getByText('Stars').last()).toBeVisible()
  })

  test('opens user profile in new window when leader button is clicked', async () => {
    await page.getByRole('button', { name: 'View Profile' }).first().click()
    await expect(page).toHaveURL('/members/arkid15r')
  })

  test('breadcrumb renders correct segments on /about', async () => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'About'])
  })

  test('renders key features section', async () => {
    await expect(page.getByText('Key Features')).toBeVisible()
    await expect(page.getByText('Advanced Community Search')).toBeVisible()
  })

  test('renders project history timeline section', async () => {
    await expect(page.getByRole('heading', { name: 'Project Timeline' })).toBeVisible()

    await expect(page.getByText('OWASP Nest Logo Introduction')).toBeVisible()

    const timelineSection = page
      .locator('div')
      .filter({ has: page.getByRole('heading', { name: 'Project Timeline' }) })
      .filter({ has: page.getByRole('button', { name: 'Show more' }) })
      .last()

    await timelineSection.getByRole('button', { name: 'Show more' }).click()

    await expect(page.getByText('Project Inception')).toBeVisible()
  })
})
