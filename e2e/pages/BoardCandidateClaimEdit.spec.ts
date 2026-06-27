import { mockClaimAuth } from '@e2e/helpers/mockClaimAuth'
import { mockSingleClaim } from '@mockData/mockClaimData'
import { test, expect } from '@playwright/test'

const baseUrl = '/board/2025/candidates/testuser/claims/experience-leadership/edit'

const mockData = {
  boardCandidateClaim: {
    __typename: 'BoardCandidateClaimNode',
    id: mockSingleClaim.key,
    ...mockSingleClaim,
  },
  updateBoardCandidateClaim: {
    __typename: 'ClaimResult',
    ok: true,
    message: 'Claim updated successfully!',
    claim: {
      __typename: 'BoardCandidateClaimNode',
      ...mockSingleClaim,
      name: 'Updated Leadership',
      description: 'Updated description',
      updatedAt: '2025-01-20T10:00:00Z',
    },
  },
}

test.describe('Board Candidate Claim Edit Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockClaimAuth(page, mockData, 'testuser', [
      'GetBoardCandidateClaim',
      'UpdateBoardCandidateClaim',
    ])
    await page.goto(baseUrl)
  })

  test('renders pre-filled form with heading and edit button', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /^Edit Claim$/ })).toBeVisible()
    await expect(page.getByRole('button', { name: /edit claim/i })).toBeVisible()
    await expect(page.getByLabel(/name/i)).toHaveValue('Leadership Experience')
    await expect(page.getByLabel(/description/i)).toHaveValue('Experience in leadership.')
  })

  test('shows access denied when viewing another user profile', async ({ page }) => {
    await mockClaimAuth(page, mockData, 'otheruser', ['GetBoardCandidateClaim'])
    await page.goto(baseUrl)
    await expect(page.getByText('Access Denied')).toBeVisible()
  })

  test('shows 404 when claim is not found', async ({ page }) => {
    await mockClaimAuth(page, { boardCandidateClaim: null }, 'testuser', [
      'GetBoardCandidateClaim',
    ])
    await page.goto(baseUrl)
    await expect(page.getByRole('heading', { level: 2, name: 'Claim Not Found' })).toBeVisible()
    await expect(
      page.getByText("Sorry, the claim you're looking for doesn't exist.")
    ).toBeVisible()
  })

  test('submits form and redirects to claim details page', async ({ page }) => {
    await page.getByLabel(/name/i).fill('Updated Leadership')
    await page.getByLabel(/description/i).fill('Updated description')
    await page.getByRole('button', { name: /edit claim/i }).click()
    await expect(page).toHaveURL(
      /\/board\/2025\/candidates\/testuser\/claims\/experience-leadership$/
    )
  })

  test('shows validation error when name is empty', async ({ page }) => {
    await page.getByLabel(/name/i).fill('')
    await page.getByRole('button', { name: /edit claim/i }).click()
    await expect(page.getByText('Name is required')).toBeVisible()
  })
})
