import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { test, expect } from '@playwright/test'

const mockSnapshots = [
  {
    id: 'snapshot_1',
    __typename: 'SnapshotNode',
    key: 'snapshot_1',
    title: 'Community Snapshot 1',
    startAt: '2024-01-01T00:00:00Z',
    endAt: '2024-01-31T00:00:00Z',
  },
]

test.describe('Community Page - Smoke Tests', () => {
  test('loads successfully with main heading and no console errors', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })
    await page.goto('/community', { timeout: 25000 })
    await expect(page.getByRole('heading', { name: 'OWASP Community' })).toBeVisible()
    await page.waitForTimeout(1000)
    expect(errors).toHaveLength(0)
  })
})

test.describe('Community Snapshots Page - Smoke Tests', () => {
  test('loads successfully with main heading and no console errors', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            snapshots: mockSnapshots,
          },
        }),
      })
    })
    await page.goto('/community/snapshots', { timeout: 25000 })
    await expect(page).toHaveTitle('Snapshots – OWASP Nest')
    await page.waitForTimeout(1000)
    expect(errors).toHaveLength(0)
  })
})

test.describe('Community Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/community', { timeout: 25000 })
  })

  test('renders main heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'OWASP Community' })).toBeVisible()
  })

  test('renders Explore Resources section', async ({ page }) => {
    await expect(page.getByText('Explore Resources')).toBeVisible()
  })

  test('renders Ways to Engage section', async ({ page }) => {
    await expect(page.getByText('Ways to Engage')).toBeVisible()
  })

  test('renders call-to-action section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Ready to Get Involved?' })).toBeVisible()
  })

  test('renders Join Slack link', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Join Slack' })).toBeVisible()
  })

  test('breadcrumb renders correct segments on /community', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Community'])
  })
})

test.describe('Community Snapshots Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            snapshots: mockSnapshots,
          },
        }),
      })
    })
    await page.goto('/community/snapshots', { timeout: 25000 })
  })

  test('renders snapshot cards from mock data', async ({ page }) => {
    await expect(
      page.getByRole('button', { name: 'View Details' }).first()
    ).toBeVisible({ timeout: 10000 })
  })

  test('displays "No Snapshots found" when there are no snapshots', async ({ page }) => {
    await page.route('**/graphql/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            snapshots: [],
          },
        }),
      })
    })
    await page.goto('/community/snapshots', { timeout: 25000 })
    await expect(page.getByText('No Snapshots found')).toBeVisible()
  })

  test('breadcrumb renders correct segments on /community/snapshots', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Community', 'Snapshots'])
  })
})
