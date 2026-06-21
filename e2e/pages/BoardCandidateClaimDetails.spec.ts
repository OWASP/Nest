import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
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
const baseUrl = '/board/2025/candidates/testuser/claims/experience-web-security'

test.describe('Board Candidate Claim Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockClaimAuth(page, mockData)
    await page.goto(baseUrl)
  })

  test('renders claim heading and claim details block', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /^Claim$/ })).toBeVisible()
    await expect(page.getByText('Web security experience')).toBeVisible()
    await expect(page.getByText('Claim Details')).toBeVisible()
  })

  test('renders evidence list with evidence items', async ({ page }) => {
    await expect(page.getByText('Evidences')).toBeVisible()
    await expect(page.getByRole('heading', { name: /^Certificate$/ })).toBeVisible()
    await expect(page.getByRole('heading', { name: /^Reference Letter$/ })).toBeVisible()
  })

  test('renders add evidence button for draft claims', async ({ page }) => {
    await expect(page.getByRole('button', { name: /add evidence/i })).toBeVisible()
  })

  test('displays empty state when no evidences exist', async ({ page }) => {
    const emptyData = {
      boardCandidateClaim: mockSingleClaim,
      boardCandidateClaimEvidences: [],
    }
    await mockClaimAuth(page, emptyData)
    await page.goto(baseUrl)
    await expect(page.getByText('No evidences.')).toBeVisible()
  })

  test('shows 404 when claim is not found', async ({ page }) => {
    const notFoundData = {
      boardCandidateClaim: null,
      boardCandidateClaimEvidences: [],
    }
    await mockClaimAuth(page, notFoundData)
    await page.goto(baseUrl)
    await expect(page.getByRole('heading', { level: 2, name: 'Claim Not Found' })).toBeVisible()
    await expect(
      page.getByText("Sorry, the claim you're looking for doesn't exist.")
    ).toBeVisible()
  })

  test('shows access denied when viewing another user profile', async ({ page }) => {
    await mockClaimAuth(page, mockData, 'otheruser')
    await page.goto(baseUrl)
    await expect(page.getByText('Access Denied')).toBeVisible()
  })

  test('breadcrumb renders correct segments', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, [
      'Home',
      'Board',
      '2025',
      'Candidates',
      'Testuser',
      'Claims',
      'Experience Web Security',
    ])
  })
})
