import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { test, expect } from '@playwright/test'

test.describe('About Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/about', { timeout: 25000 })
  })

  test('renders main sections correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'About' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Project Timeline' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Our Story' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Leaders' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Roadmap' })).toBeVisible()
  })

  test('displays contributor information when data is loaded', async ({ page }) => {
    await expect(page.getByText('Ahmed Gouda', { exact: true })).toBeVisible()
    await expect(page.getByText('Abhay Mishra', { exact: true })).toBeVisible()
    await expect(page.getByText('Raj gupta', { exact: true })).toBeVisible()
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
    await expect(page.getByRole('heading', { name: 'Roadmap' })).toBeVisible()

    await expect(page.getByText('Enhance OWASP Nest Availability and Performance')).toBeVisible()
    await expect(
      page.getByText(
        'This milestone focuses on modernizing OWASP Nest to improve reliability, scalability, and availability. It includes migrating the Django + Ninja backend to AWS Lambda using Zappa, with static/media served via S3 and long-running tasks adapted for serverless execution. In parallel, a PoC for Infrastructure as Code will provision and manage key components - Lambda, ECS/Fargate, S3, RDS, Redis, and an EC2 instance for nightly syncs - using Terraform or an alternative tool.'
      )
    ).toBeVisible()

    const roadmapSection = page
      .locator('div')
      .filter({ has: page.getByRole('heading', { name: 'Roadmap' }) })
      .filter({ has: page.getByRole('button', { name: 'Show more' }) })
      .last()

    await roadmapSection.getByRole('button', { name: 'Show more' }).click()
  })

  test('displays project statistics', async ({ page }) => {
    await expect(page.getByText('Contributors').last()).toBeVisible()
    await expect(page.getByText('Open Issues').last()).toBeVisible()
    await expect(page.getByText('Forks').last()).toBeVisible()
    await expect(page.getByText('Stars').last()).toBeVisible()
  })

  test('breadcrumb renders correct segments on /about', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'About'])
  })

  test('renders key features section', async ({ page }) => {
    await expect(page.getByText('Key Features')).toBeVisible()
    await expect(page.getByText('Advanced Community Search')).toBeVisible()
  })

  test('renders project history timeline section', async ({ page }) => {
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

  test('opens user profile in new window when leader button is clicked', async ({ page }) => {
    await page.getByRole('button', { name: 'View Profile' }).first().click()
    await expect(page).toHaveURL('/members/arkid15r')
  })
})
