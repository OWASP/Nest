import { test, expect } from '@playwright/test'
import { Page, Route } from '@playwright/test'

const MOCK_SNAPSHOTS = [
  {
    key: 'snapshot-q1-2024',
    title: 'Community Snapshot Q1 2024',
    startAt: '2024-01-01T00:00:00Z',
    endAt: '2024-03-31T00:00:00Z',
  },
  {
    key: 'snapshot-q2-2024',
    title: 'Community Snapshot Q2 2024',
    startAt: '2024-04-01T00:00:00Z',
    endAt: '2024-06-30T00:00:00Z',
  },
]


const mockGraphQL = async <T>(
  page: Page,
  body: { data?: any; errors?: { message: string }[] }
) => {
  await page.route('**/graphql**', async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(body),
    })
  })
}

test.describe('Snapshots Page', () => {
  test('renders skeleton while loading', async ({ page }) => {
    await page.route('**/graphql/**', () => {})
    await page.goto('/community/snapshots')
    await expect(page.locator('output')).toHaveCount(12)
  })

  test('renders snapshot cards on successful load', async ({ page }) => {
    await mockGraphQL(page, { data: { snapshots: MOCK_SNAPSHOTS } })
    await page.goto('/community/snapshots')

    for (const { title } of MOCK_SNAPSHOTS) {
      await expect(page.getByText(title)).toBeVisible()
    }
  })

  test('renders empty state when no snapshots returned', async ({ page }) => {
    await mockGraphQL(page, { data: { snapshots: [] } })
    await page.goto('/community/snapshots')
    await expect(page.getByText('No Snapshots found')).toBeVisible()
  })

  test('shows error toast on GraphQL failure', async ({ page }) => {
    await mockGraphQL(page, { errors: [{ message: 'Internal server error' }] })
    await page.goto('/community/snapshots')
    await expect(page.getByText('GraphQL Request Failed')).toBeVisible()
    await expect(page.getByText('Unable to complete the requested operation.')).toBeVisible()
  })
})