import { mockClaimAuth } from '@e2e/helpers/mockClaimAuth'
import { mockSingleClaim, mockEvidences } from '@mockData/mockClaimData'
import { test, expect } from '@playwright/test'

const mockData = {
  boardCandidateClaim: { __typename: 'BoardCandidateClaimNode', id: mockSingleClaim.key, ...mockSingleClaim },
  boardCandidateClaimEvidences: mockEvidences.map((e) => ({
    __typename: 'BoardCandidateClaimEvidenceNode',
    id: e.key,
    ...e,
  })),
}
const baseUrl = '/board/2025/candidates/testuser/claims/experience-leadership/evidences/certificate'

test.describe('Board Candidate Claim Evidence Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockClaimAuth(page, mockData, 'testuser', ['GetClaimAndEvidences'])
    await page.goto(baseUrl)
  })

  test('renders evidence heading and evidence details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /^Evidence$/ })).toBeVisible()
    await expect(page.getByText(/Name.*Certificate/i)).toBeVisible()
    await expect(page.getByText('Evidence Details')).toBeVisible()
  })

  test('renders download evidence button when evidence has file', async ({ page }) => {
    await expect(page.getByRole('button', { name: /download evidence/i })).toBeVisible()
  })

  test('does not render download button when evidence has no file', async ({ page }) => {
    const noFileMockData = {
      boardCandidateClaim: { __typename: 'BoardCandidateClaimNode', id: mockSingleClaim.key, ...mockSingleClaim },
      boardCandidateClaimEvidences: [
        {
          __typename: 'BoardCandidateClaimEvidenceNode',
          id: 'reference-letter',
          ...mockEvidences[1],
        },
      ],
    }
    await mockClaimAuth(page, noFileMockData, 'testuser', ['GetClaimAndEvidences'])
    await page.goto('/board/2025/candidates/testuser/claims/experience-leadership/evidences/reference-letter')
    await expect(page.getByRole('button', { name: /download evidence/i })).not.toBeVisible()
  })

  test('shows 404 when evidence is not found', async ({ page }) => {
    const notFoundData = {
      boardCandidateClaim: { __typename: 'BoardCandidateClaimNode', id: mockSingleClaim.key, ...mockSingleClaim },
      boardCandidateClaimEvidences: [],
    }
    await mockClaimAuth(page, notFoundData, 'testuser', ['GetClaimAndEvidences'])
    await page.goto(baseUrl)
    await expect(page.getByRole('heading', { level: 2, name: 'Evidence Not Found' })).toBeVisible()
    await expect(
      page.getByText("Sorry, the evidence you're looking for doesn't exist.")
    ).toBeVisible()
  })

  test('shows access denied when viewing another user profile', async ({ page }) => {
    await mockClaimAuth(page, mockData, 'otheruser', ['GetClaimAndEvidences'])
    await page.goto(baseUrl)
    await expect(page.getByText('Access Denied')).toBeVisible()
  })
})
