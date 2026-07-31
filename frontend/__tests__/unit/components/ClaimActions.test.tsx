import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useRouter } from 'next/navigation'
import {
  DiscardBoardCandidateClaimDocument,
  SubmitBoardCandidateClaimDocument,
  WithdrawBoardCandidateClaimDocument,
} from 'types/__generated__/claimMutations.generated'
import { ClaimStatusEnum, ReviewStatusEnum } from 'types/__generated__/graphql'
import { CreateBoardCandidateClaimReviewDocument } from 'types/__generated__/reviewMutations.generated'
import { GetClaimsAndReviewsDocument } from 'types/__generated__/reviewQueries.generated'
import type { Claim } from 'types/claim'
import ClaimActions from 'components/ClaimActions'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(),
}))

const mockUseDjangoSession = useDjangoSession as jest.Mock

const mockSubmit = jest.fn()
const mockDiscard = jest.fn()
const mockWithdraw = jest.fn()
const mockReview = jest.fn()

const baseClaim: Claim = {
  __typename: 'BoardCandidateClaimNode',
  id: 'claim-1',
  key: 'test-claim',
  name: 'Test Claim',
  description: 'Test description',
  status: ClaimStatusEnum.Draft,
  createdAt: '2025-01-15T10:00:00Z',
  updatedAt: '2025-01-15T10:00:00Z',
  hasEvidence: false,
  order: 1,
}

const renderClaimActions = (claim: Claim) =>
  render(
    <ClaimActions
      claim={claim}
      login="testuser"
      year="2025"
      hasReviewed={false}
      isReviewer={undefined}
    />
  )

const renderAsReviewer = (claim: Claim) =>
  render(
    <ClaimActions
      claim={claim}
      login="testuser"
      year="2025"
      hasReviewed={false}
      isReviewer={true}
    />
  )

const openDropdown = (label: string) => {
  fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
  fireEvent.click(screen.getByText(label))
}

describe('ClaimActions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useMutation as unknown as jest.Mock).mockImplementation((doc) => {
      if (doc === SubmitBoardCandidateClaimDocument) return [mockSubmit, {}]
      if (doc === DiscardBoardCandidateClaimDocument) return [mockDiscard, {}]
      if (doc === WithdrawBoardCandidateClaimDocument) return [mockWithdraw, {}]
      if (doc === CreateBoardCandidateClaimReviewDocument) return [mockReview, {}]
      return [jest.fn(), {}]
    })
    mockUseDjangoSession.mockReturnValue({
      session: { user: { login: 'testuser' } },
    })
  })

  describe('renders correct options per status', () => {
    it('shows edit, submit, and discard for DRAFT', () => {
      renderClaimActions(baseClaim)

      const button = screen.getByRole('button', { name: /actions menu/i })
      expect(button).toBeInTheDocument()

      fireEvent.click(button)
      expect(screen.getByText('Edit Claim')).toBeInTheDocument()
      expect(screen.getByText('Submit Claim')).toBeInTheDocument()
      expect(screen.getByText('Discard Claim')).toBeInTheDocument()
    })

    it('shows withdraw for SUBMITTED', () => {
      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Submitted })

      fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
      expect(screen.getByText('Withdraw Claim')).toBeInTheDocument()
      expect(screen.queryByText('Edit Claim')).not.toBeInTheDocument()
    })

    it('shows withdraw for APPROVED', () => {
      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Approved })

      fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
      expect(screen.getByText('Withdraw Claim')).toBeInTheDocument()
    })

    it('shows no dropdown for REJECTED', () => {
      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Rejected })
      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
    })

    it('shows no dropdown for DISCARDED', () => {
      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Discarded })
      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
    })

    it('shows no dropdown for WITHDRAWN', () => {
      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Withdrawn })
      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
    })

    it('shows no dropdown for unknown status', () => {
      renderClaimActions({ ...baseClaim, status: 'UNKNOWN' as ClaimStatusEnum })
      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
    })

    it('shows approve and reject for SUBMITTED when reviewer', () => {
      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })

      fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
      expect(screen.getByText('Approve Claim')).toBeInTheDocument()
      expect(screen.getByText('Reject Claim')).toBeInTheDocument()
    })

    it('hides standard actions when reviewer', () => {
      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })

      fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
      expect(screen.queryByText('Submit Claim')).not.toBeInTheDocument()
      expect(screen.queryByText('Discard Claim')).not.toBeInTheDocument()
      expect(screen.queryByText('Withdraw Claim')).not.toBeInTheDocument()
    })

    it('hides reviewer actions when hasReviewed is true', () => {
      render(
        <ClaimActions
          claim={{ ...baseClaim, status: ClaimStatusEnum.Submitted }}
          login="testuser"
          year="2025"
          hasReviewed={true}
          isReviewer={true}
        />
      )

      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
    })

    it('shows only edit option for DRAFT when reviewer', () => {
      renderAsReviewer(baseClaim)

      fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
      expect(screen.getByText('Edit Claim')).toBeInTheDocument()
      expect(screen.queryByText('Submit Claim')).not.toBeInTheDocument()
      expect(screen.queryByText('Discard Claim')).not.toBeInTheDocument()
    })

    it('hides dropdown for non-DRAFT non-SUBMITTED statuses when reviewer', () => {
      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Rejected })

      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
    })
  })

  describe('submit action', () => {
    it('submits claim and navigates on success', async () => {
      const mockPush = (useRouter as jest.Mock)().push
      mockSubmit.mockResolvedValue({
        data: {
          submitBoardCandidateClaim: { ok: true, claim: { ...baseClaim, status: 'SUBMITTED' } },
        },
      })

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      expect(screen.getByText('Submit Claim')).toBeInTheDocument()

      fireEvent.click(screen.getByText('Submit'))
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: { input: { key: 'test-claim', year: 2025 } },
          })
        )
      })
      expect(mockPush).toHaveBeenCalledWith('/board/2025/candidates/testuser/claims')
    })

    it('shows error toast when submit returns ok: false', async () => {
      mockSubmit.mockResolvedValue({
        data: { submitBoardCandidateClaim: { ok: false, message: 'Already submitted' } },
      })

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      fireEvent.click(screen.getByText('Submit'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Already submitted', color: 'danger' })
        )
      })
    })

    it('shows error toast when submit returns ok: false with fallback message', async () => {
      mockSubmit.mockResolvedValue({
        data: { submitBoardCandidateClaim: { ok: false } },
      })

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      fireEvent.click(screen.getByText('Submit'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Submit failed.', color: 'danger' })
        )
      })
    })

    it('shows error toast on mutation failure', async () => {
      mockSubmit.mockRejectedValue(new Error('Network error'))

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      fireEvent.click(screen.getByText('Submit'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Network error', color: 'danger' })
        )
      })
    })
  })

  describe('discard action', () => {
    it('discards claim and navigates on success', async () => {
      const mockPush = (useRouter as jest.Mock)().push
      const mockCache = { readQuery: jest.fn(), writeQuery: jest.fn() }
      mockDiscard.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: {
              discardBoardCandidateClaim: {
                ok: true,
                claim: { ...baseClaim, status: 'DISCARDED' },
              },
            },
          })
        return Promise.resolve({
          data: {
            discardBoardCandidateClaim: { ok: true, claim: { ...baseClaim, status: 'DISCARDED' } },
          },
        })
      })

      renderClaimActions(baseClaim)
      openDropdown('Discard Claim')
      fireEvent.click(screen.getByText('Discard'))

      await waitFor(() => {
        expect(mockDiscard).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: { input: { key: 'test-claim', year: 2025 } },
          })
        )
      })
      expect(mockPush).toHaveBeenCalledWith('/board/2025/candidates/testuser/claims')
    })

    it('shows error toast when discard returns ok: false', async () => {
      mockDiscard.mockResolvedValue({
        data: { discardBoardCandidateClaim: { ok: false, message: 'Cannot discard' } },
      })

      renderClaimActions(baseClaim)
      openDropdown('Discard Claim')
      fireEvent.click(screen.getByText('Discard'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Cannot discard', color: 'danger' })
        )
      })
    })

    it('shows error toast when discard returns ok: false with fallback message', async () => {
      mockDiscard.mockResolvedValue({
        data: { discardBoardCandidateClaim: { ok: false } },
      })

      renderClaimActions(baseClaim)
      openDropdown('Discard Claim')
      fireEvent.click(screen.getByText('Discard'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Discard failed.', color: 'danger' })
        )
      })
    })
  })

  describe('withdraw action', () => {
    it('withdraws claim with reason and navigates on success', async () => {
      const mockPush = (useRouter as jest.Mock)().push
      const mockCache = { readQuery: jest.fn(), writeQuery: jest.fn() }
      mockWithdraw.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: {
              withdrawBoardCandidateClaim: {
                ok: true,
                claim: { ...baseClaim, status: 'WITHDRAWN' },
              },
            },
          })
        return Promise.resolve({
          data: {
            withdrawBoardCandidateClaim: { ok: true, claim: { ...baseClaim, status: 'WITHDRAWN' } },
          },
        })
      })

      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Withdraw Claim')

      const textarea = screen.getByLabelText('Reason for withdrawal')
      fireEvent.change(textarea, { target: { value: 'Personal reasons' } })
      fireEvent.click(screen.getByText('Withdraw'))

      await waitFor(() => {
        expect(mockWithdraw).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: {
              input: { key: 'test-claim', withdrawnReason: 'Personal reasons', year: 2025 },
            },
          })
        )
      })
      expect(mockPush).toHaveBeenCalledWith('/board/2025/candidates/testuser/claims')
    })

    it('shows error toast when withdraw returns ok: false', async () => {
      mockWithdraw.mockResolvedValue({
        data: { withdrawBoardCandidateClaim: { ok: false, message: 'Already withdrawn' } },
      })

      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Withdraw Claim')
      fireEvent.click(screen.getByText('Withdraw'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Already withdrawn', color: 'danger' })
        )
      })
    })

    it('shows error toast when withdraw returns ok: false with fallback message', async () => {
      mockWithdraw.mockResolvedValue({
        data: { withdrawBoardCandidateClaim: { ok: false } },
      })

      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Withdraw Claim')
      fireEvent.click(screen.getByText('Withdraw'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Withdraw failed.', color: 'danger' })
        )
      })
    })
  })

  describe('approve/reject action', () => {
    it('approves claim with notes and navigates to review page', async () => {
      const mockPush = (useRouter as jest.Mock)().push
      mockReview.mockResolvedValue({
        data: {
          createBoardCandidateClaimReview: {
            ok: true,
            review: {
              __typename: 'BoardCandidateClaimReviewNode',
              id: 'review-1',
              createdAt: '2025-02-01T10:00:00Z',
              status: ReviewStatusEnum.Approved,
              notes: 'Looks good',
            },
          },
        },
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')

      const textarea = screen.getByLabelText('Notes')
      fireEvent.change(textarea, { target: { value: 'Looks good' } })
      fireEvent.click(screen.getByText('Approve'))

      await waitFor(() => {
        expect(mockReview).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: {
              input: {
                claimKey: 'test-claim',
                claimMemberLogin: 'testuser',
                notes: 'Looks good',
                status: ReviewStatusEnum.Approved,
                year: 2025,
              },
            },
          })
        )
      })
      expect(mockPush).toHaveBeenCalledWith('/board/2025/review')
    })

    it('rejects claim with notes and navigates to review page', async () => {
      const mockPush = (useRouter as jest.Mock)().push
      mockReview.mockResolvedValue({
        data: {
          createBoardCandidateClaimReview: {
            ok: true,
            review: {
              __typename: 'BoardCandidateClaimReviewNode',
              id: 'review-2',
              createdAt: '2025-02-01T10:00:00Z',
              status: ReviewStatusEnum.Rejected,
              notes: 'Not sufficient',
            },
          },
        },
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Reject Claim')

      const textarea = screen.getByLabelText('Notes')
      fireEvent.change(textarea, { target: { value: 'Not sufficient' } })
      fireEvent.click(screen.getByText('Reject'))

      await waitFor(() => {
        expect(mockReview).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: {
              input: {
                claimKey: 'test-claim',
                claimMemberLogin: 'testuser',
                notes: 'Not sufficient',
                status: ReviewStatusEnum.Rejected,
                year: 2025,
              },
            },
          })
        )
      })
      expect(mockPush).toHaveBeenCalledWith('/board/2025/review')
    })

    it('shows error toast when approve returns ok: false', async () => {
      mockReview.mockResolvedValue({
        data: { createBoardCandidateClaimReview: { ok: false, message: 'Already reviewed' } },
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')
      fireEvent.click(screen.getByText('Approve'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Already reviewed', color: 'danger' })
        )
      })
    })

    it('shows error toast when approve returns ok: false with fallback message', async () => {
      mockReview.mockResolvedValue({
        data: { createBoardCandidateClaimReview: { ok: false } },
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')
      fireEvent.click(screen.getByText('Approve'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Approve failed.', color: 'danger' })
        )
      })
    })

    it('shows error toast when reject returns ok: false', async () => {
      mockReview.mockResolvedValue({
        data: { createBoardCandidateClaimReview: { ok: false, message: 'Already reviewed' } },
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Reject Claim')
      fireEvent.click(screen.getByText('Reject'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Already reviewed', color: 'danger' })
        )
      })
    })

    it('shows error toast on mutation failure', async () => {
      mockReview.mockRejectedValue(new Error('Review failed'))

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')
      fireEvent.click(screen.getByText('Approve'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Review failed', color: 'danger' })
        )
      })
    })

    it('shows Notes textarea in modal for approve', () => {
      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')

      expect(screen.getByLabelText('Notes')).toBeInTheDocument()
    })

    it('shows Notes textarea in modal for reject', () => {
      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Reject Claim')

      expect(screen.getByLabelText('Notes')).toBeInTheDocument()
    })
  })

  describe('modal behavior', () => {
    it('opens modal when submit is clicked', () => {
      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')

      expect(screen.getByText(/Are you sure you want to submit/i)).toBeInTheDocument()
    })

    it('opens modal with reason textarea for withdraw', () => {
      renderClaimActions({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Withdraw Claim')

      expect(screen.getByLabelText('Reason for withdrawal')).toBeInTheDocument()
    })

    it('closes modal when Cancel is clicked', async () => {
      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      expect(screen.getByText(/Are you sure/i)).toBeInTheDocument()

      fireEvent.click(screen.getByText('Cancel'))

      await waitFor(() => {
        expect(screen.queryByText(/Are you sure/i)).not.toBeInTheDocument()
      })
    })

    it('closes modal when X is clicked', async () => {
      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')

      const closeButton = screen.getByRole('button', { name: /close/i })
      fireEvent.click(closeButton)

      await waitFor(() => {
        expect(screen.queryByText(/Are you sure/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('edit navigation', () => {
    it('navigates to edit page when Edit Claim is clicked', () => {
      const mockPush = (useRouter as jest.Mock)().push
      renderClaimActions(baseClaim)

      const button = screen.getByRole('button', { name: /actions menu/i })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      fireEvent.click(screen.getByText('Edit Claim'))
      expect(mockPush).toHaveBeenCalledWith(
        '/board/2025/candidates/testuser/claims/test-claim/edit'
      )
    })
  })

  describe('error handling - non-Error thrown values', () => {
    it('handles non-Error thrown values gracefully', async () => {
      mockSubmit.mockRejectedValue('string error')

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      fireEvent.click(screen.getByText('Submit'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Claim action failed.' })
        )
      })
    })
  })

  describe('updateClaimsCache', () => {
    it('handles cache update when existing data is present', async () => {
      const mockCache = {
        readQuery: jest.fn().mockReturnValue({
          boardCandidateClaims: [
            { key: 'test-claim', name: 'Old Name' },
            { key: 'other-claim', name: 'Other' },
          ],
        }),
        writeQuery: jest.fn(),
      }

      const updatedClaim = { key: 'test-claim', name: 'Updated Name' }
      mockSubmit.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: { submitBoardCandidateClaim: { ok: true, claim: updatedClaim } },
          })
        return Promise.resolve({
          data: { submitBoardCandidateClaim: { ok: true, claim: updatedClaim } },
        })
      })

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      fireEvent.click(screen.getByText('Submit'))

      await waitFor(() => {
        expect(mockCache.writeQuery).toHaveBeenCalledWith(
          expect.objectContaining({
            data: {
              boardCandidateClaims: [
                { key: 'test-claim', name: 'Updated Name' },
                { key: 'other-claim', name: 'Other' },
              ],
            },
          })
        )
      })
    })

    it('skips cache update when readQuery returns null', async () => {
      const mockCache = {
        readQuery: jest.fn().mockReturnValue(null),
        writeQuery: jest.fn(),
      }

      mockSubmit.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, { data: { submitBoardCandidateClaim: { ok: true, claim: {} } } })
        return Promise.resolve({
          data: { submitBoardCandidateClaim: { ok: true, claim: {} } },
        })
      })

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      fireEvent.click(screen.getByText('Submit'))

      await waitFor(() => {
        expect(mockCache.readQuery).toHaveBeenCalled()
        expect(mockCache.writeQuery).not.toHaveBeenCalled()
      })
    })

    it('skips cache update when mutation returns no claim', async () => {
      const mockCache = {
        readQuery: jest.fn(),
        writeQuery: jest.fn(),
      }

      mockSubmit.mockImplementation(({ update }) => {
        if (update) update(mockCache, { data: { submitBoardCandidateClaim: { ok: true } } })
        return Promise.resolve({
          data: { submitBoardCandidateClaim: { ok: true } },
        })
      })

      renderClaimActions(baseClaim)
      openDropdown('Submit Claim')
      fireEvent.click(screen.getByText('Submit'))

      await waitFor(() => {
        expect(mockCache.readQuery).not.toHaveBeenCalled()
        expect(mockCache.writeQuery).not.toHaveBeenCalled()
      })
    })
  })

  describe('updateReviewsCache', () => {
    it('adds review to matching claim in cache', async () => {
      const existingClaim = {
        key: 'test-claim',
        name: 'Test Claim',
        reviews: [],
      }
      const otherClaim = {
        key: 'other-claim',
        name: 'Other',
        reviews: [],
      }
      const mockCache = {
        readQuery: jest.fn().mockReturnValue({
          boardCandidateClaims: [existingClaim, otherClaim],
        }),
        writeQuery: jest.fn(),
      }

      const newReview = {
        __typename: 'BoardCandidateClaimReviewNode',
        id: 'review-1',
        createdAt: '2025-02-01T10:00:00Z',
        status: ReviewStatusEnum.Approved,
        notes: 'Looks good',
      }
      mockReview.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: {
              createBoardCandidateClaimReview: {
                ok: true,
                review: newReview,
              },
            },
          })
        return Promise.resolve({
          data: {
            createBoardCandidateClaimReview: {
              ok: true,
              review: newReview,
            },
          },
        })
      })

      mockUseDjangoSession.mockReturnValue({
        session: { user: { login: 'reviewer' } },
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')
      fireEvent.click(screen.getByText('Approve'))

      await waitFor(() => {
        expect(mockCache.writeQuery).toHaveBeenCalledWith(
          expect.objectContaining({
            query: GetClaimsAndReviewsDocument,
            variables: { sessionLogin: 'reviewer', year: 2025 },
            data: {
              boardCandidateClaims: [
                {
                  ...existingClaim,
                  reviews: [
                    {
                      __typename: 'BoardCandidateClaimReviewNode',
                      id: 'review-1',
                      createdAt: '2025-02-01T10:00:00Z',
                      status: ReviewStatusEnum.Approved,
                      reviewer: { __typename: 'UserNode', login: 'reviewer' },
                    },
                  ],
                },
                otherClaim,
              ],
            },
          })
        )
      })
    })

    it('skips cache update when readQuery returns null', async () => {
      const newReview = {
        __typename: 'BoardCandidateClaimReviewNode',
        id: 'review-1',
        createdAt: '2025-02-01T10:00:00Z',
        status: ReviewStatusEnum.Approved,
        notes: 'Looks good',
      }
      const mockCache = {
        readQuery: jest.fn().mockReturnValue(null),
        writeQuery: jest.fn(),
      }

      mockReview.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: { createBoardCandidateClaimReview: { ok: true, review: newReview } },
          })
        return Promise.resolve({
          data: { createBoardCandidateClaimReview: { ok: true, review: newReview } },
        })
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')
      fireEvent.click(screen.getByText('Approve'))

      await waitFor(() => {
        expect(mockCache.readQuery).toHaveBeenCalled()
        expect(mockCache.writeQuery).not.toHaveBeenCalled()
      })
    })

    it('skips cache update when mutation returns no review', async () => {
      const mockCache = {
        readQuery: jest.fn(),
        writeQuery: jest.fn(),
      }

      mockReview.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: { createBoardCandidateClaimReview: { ok: true } },
          })
        return Promise.resolve({
          data: { createBoardCandidateClaimReview: { ok: true } },
        })
      })

      renderAsReviewer({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      openDropdown('Approve Claim')
      fireEvent.click(screen.getByText('Approve'))

      await waitFor(() => {
        expect(mockCache.readQuery).not.toHaveBeenCalled()
        expect(mockCache.writeQuery).not.toHaveBeenCalled()
      })
    })
  })
})
