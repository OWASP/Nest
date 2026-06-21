import { expectBreadCrumbsToBeVisible } from '@e2e/helpers/expects'
import { mockClaimAuth } from '@e2e/helpers/mockClaimAuth'
import { mockClaims, mockCandidateData } from '@mockData/mockClaimData'
import { test, expect } from '@playwright/test'

const mockData = {
  boardCandidateClaims: mockClaims.map((c) => ({ __typename: 'BoardCandidateClaimNode', id: c.key, ...c })),
  ...mockCandidateData,
}
const baseUrl = '/board/2025/candidates/testuser/claims'

test.describe('Board Candidate Claims Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockClaimAuth(page, mockData, 'testuser', ['GetBoardCandidateAndClaims'])
    await page.goto(baseUrl)
  })

  test('renders claims page with heading and create button', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /^Claims$/ })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create Claim' })).toBeVisible()
  })

  test('renders claims grouped by status sections', async ({ page }) => {
    await expect(page.getByText('Draft Claims')).toBeVisible()
    await expect(page.getByText('Submitted Claims')).toBeVisible()
    await expect(page.getByText('Approved Claims')).toBeVisible()
    await expect(page.getByText('Rejected Claims')).toBeVisible()
    await expect(page.getByText('Withdrawn Claims')).toBeVisible()
  })

  test('renders claim names and evidence badges', async ({ page }) => {
    await expect(page.getByText('Leadership Experience')).toBeVisible()
    await expect(page.getByText('Chapter Leadership')).toBeVisible()
    await expect(page.getByRole('heading', { name: /^Approved Claim$/ })).toBeVisible()
    await expect(page.getByText('Evidence').first()).toBeVisible()
  })

  test('displays empty state when no claims exist', async ({ page }) => {
    const emptyData = { boardCandidateClaims: [], ...mockCandidateData }
    await mockClaimAuth(page, emptyData, 'testuser', ['GetBoardCandidateAndClaims'])
    await page.goto(baseUrl)
    await expect(page.getByText('No draft claims.')).toBeVisible()
    await expect(page.getByText('No submitted claims.')).toBeVisible()
    await expect(page.getByText('No approved claims.')).toBeVisible()
    await expect(page.getByText('No rejected claims.')).toBeVisible()
    await expect(page.getByText('No withdrawn claims.')).toBeVisible()
  })

  test('shows access denied when viewing another user profile', async ({ page }) => {
    await mockClaimAuth(page, mockData, 'otheruser', ['GetBoardCandidateAndClaims'])
    await page.goto(baseUrl)
    await expect(page.getByText('Access Denied')).toBeVisible()
  })

  test('breadcrumb renders correct segments', async ({ page }) => {
    await expectBreadCrumbsToBeVisible(page, ['Home', 'Board', '2025', 'Candidates', 'Testuser', 'Claims'])
  })
})
