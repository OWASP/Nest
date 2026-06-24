import { mockClaimAuth } from '@e2e/helpers/mockClaimAuth'
import { mockCandidateData } from '@mockData/mockClaimData'
import { test, expect } from '@playwright/test'

const baseUrl = '/board/2025/candidates/testuser/claims/create'
const mockData = {
  ...mockCandidateData,
  createBoardCandidateClaim: {
    __typename: 'CreateBoardCandidateClaimResult',
    ok: true,
    message: 'Claim created successfully!',
    claim: {
      __typename: 'BoardCandidateClaimNode',
      id: 'new-claim',
      key: 'new-claim',
      name: 'Test Claim',
      description: 'Test description',
      hasEvidence: false,
      order: 1,
      status: 'DRAFT',
      createdAt: '2025-01-15T10:00:00Z',
      updatedAt: '2025-01-15T10:00:00Z',
    },
  },
}

test.describe('Board Candidate Claim Create Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockClaimAuth(page, mockData, 'testuser', [
      'GetBoardCandidate',
      'CreateBoardCandidateClaim',
    ])
    await page.goto(baseUrl)
  })

  test('renders form with heading and submit button', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /^Create Claim$/ })).toBeVisible()
    await expect(page.getByRole('button', { name: /create claim/i })).toBeVisible()
  })

  test('shows access denied when viewing another user profile', async ({ page }) => {
    await mockClaimAuth(page, {}, 'otheruser')
    await page.goto(baseUrl)
    await expect(page.getByText('Access Denied')).toBeVisible()
    await expect(page.getByText('You must be a candidate to create a claim.')).toBeVisible()
  })

  test('submits form and redirects to claims page', async ({ page }) => {
    await page.getByLabel(/name/i).fill('New Claim')
    await page.getByLabel(/description/i).fill('New claim description')
    await page.getByRole('button', { name: /create claim/i }).click()
    await expect(page).toHaveURL(/\/board\/2025\/candidates\/testuser\/claims$/)
  })

  test('shows validation error when name is empty', async ({ page }) => {
    await page.getByRole('button', { name: /create claim/i }).click()
    await expect(page.getByText('Name is required')).toBeVisible()
  })
})
