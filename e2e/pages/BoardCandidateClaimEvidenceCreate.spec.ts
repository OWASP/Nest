import { mockClaimAuth } from '@e2e/helpers/mockClaimAuth'
import { test, expect } from '@playwright/test'

const baseUrl = '/board/2025/candidates/testuser/claims/experience-leadership/evidences/create'
const mockData = {
  createBoardCandidateClaimEvidence: {
    __typename: 'CreateBoardCandidateClaimEvidenceResult',
    ok: true,
    message: 'Evidence created successfully!',
    evidence: {
      __typename: 'BoardCandidateClaimEvidenceNode',
      id: 'new-evidence',
      key: 'new-evidence',
      name: 'Test Evidence',
      description: 'Test description',
      sourceUrl: 'https://example.com/test',
      hasFile: false,
      createdAt: '2025-01-16T10:00:00Z',
      updatedAt: '2025-01-16T10:00:00Z',
    },
  },
}

test.describe('Board Candidate Claim Evidence Create Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockClaimAuth(page, mockData, 'testuser', ['CreateBoardCandidateClaimEvidence'])
    await page.goto(baseUrl)
  })

  test('renders form with heading and submit button', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /^Add Evidence$/ })).toBeVisible()
    await expect(page.getByRole('button', { name: /add evidence/i })).toBeVisible()
  })

  test('shows access denied when viewing another user profile', async ({ page }) => {
    await mockClaimAuth(page, {}, 'otheruser', ['CreateBoardCandidateClaimEvidence'])
    await page.goto(baseUrl)
    await expect(page.getByText('Access Denied')).toBeVisible()
    await expect(page.getByText('You must be a candidate to add an evidence.')).toBeVisible()
  })

  test('submits form and redirects to claim details page', async ({ page }) => {
    await page.getByLabel(/name/i).fill('New Evidence')
    await page.getByLabel(/description/i).fill('New evidence description')
    await page.getByLabel(/source url/i).fill('https://example.com/evidence')
    await page.getByRole('button', { name: /add evidence/i }).click()
    await expect(page).toHaveURL(/\/board\/2025\/candidates\/testuser\/claims\/experience-leadership$/)
  })

  test('shows validation error when source url and file are both empty', async ({ page }) => {
    await page.getByLabel(/name/i).fill('Test')
    await page.getByLabel(/description/i).fill('Test description')
    await page.getByRole('button', { name: /add evidence/i }).click()
    await expect(page.getByText('Either a file or source URL is required.')).toBeVisible()
  })
})
