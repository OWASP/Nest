import { mockClaimAuth } from '@e2e/helpers/mockClaimAuth'
import { mockEvidences } from '@mockData/mockClaimData'
import { test, expect } from '@playwright/test'

const certificateEvidence = {
  __typename: 'BoardCandidateClaimEvidenceNode',
  id: 'certificate',
  ...mockEvidences[0],
}

const baseUrl = '/board/2025/candidates/testuser/claims/experience-leadership/evidences/certificate/edit'

const mockData = {
  boardCandidateClaimEvidence: certificateEvidence,
  updateBoardCandidateClaimEvidence: {
    __typename: 'UpdateBoardCandidateClaimEvidenceResult',
    ok: true,
    message: 'Evidence updated successfully!',
    evidence: {
      ...certificateEvidence,
      name: 'Updated Certificate',
      description: 'Updated description',
      updatedAt: '2025-01-20T10:00:00Z',
    },
  },
}

test.describe('Board Candidate Claim Evidence Edit Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockClaimAuth(page, mockData, 'testuser', [
      'GetBoardCandidateClaimEvidence',
      'UpdateBoardCandidateClaimEvidence',
    ])
    await page.goto(baseUrl)
  })

  test('renders pre-filled form with heading and update button', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /^Edit Evidence$/ })).toBeVisible()
    await expect(page.getByRole('button', { name: /update evidence/i })).toBeVisible()
    await expect(page.getByLabel(/name/i)).toHaveValue('Certificate')
    await expect(page.getByLabel(/description/i)).toHaveValue('Certificate of completion.')
  })

  test('shows access denied when viewing another user profile', async ({ page }) => {
    await mockClaimAuth(page, mockData, 'otheruser', [
      'GetBoardCandidateClaimEvidence',
      'UpdateBoardCandidateClaimEvidence',
    ])
    await page.goto(baseUrl)
    await expect(page.getByText('Access Denied')).toBeVisible()
  })

  test('shows 404 when evidence is not found', async ({ page }) => {
    await mockClaimAuth(page, { boardCandidateClaimEvidence: null }, 'testuser', [
      'GetBoardCandidateClaimEvidence',
    ])
    await page.goto(baseUrl)
    await expect(page.getByRole('heading', { level: 2, name: 'Evidence Not Found' })).toBeVisible()
    await expect(
      page.getByText("Sorry, the evidence you're looking for doesn't exist.")
    ).toBeVisible()
  })

  test('submits form and redirects to evidence details page', async ({ page }) => {
    await page.getByLabel(/name/i).fill('Updated Certificate')
    await page.getByLabel(/source url/i).fill('https://example.com/updated')
    await page.getByRole('button', { name: /update evidence/i }).click()
    await expect(page).toHaveURL(
      /\/board\/2025\/candidates\/testuser\/claims\/experience-leadership\/evidences\/certificate$/
    )
  })

  test('shows validation error when name is empty', async ({ page }) => {
    await page.getByLabel(/name/i).fill('')
    await page.getByRole('button', { name: /update evidence/i }).click()
    await expect(page.getByText('Name is required')).toBeVisible()
  })
})
