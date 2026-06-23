import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import {
  DiscardBoardCandidateClaimDocument,
  SubmitBoardCandidateClaimDocument,
  WithdrawBoardCandidateClaimDocument,
} from 'types/__generated__/claimMutations.generated'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
import type { Claim } from 'types/claim'
import ClaimActions from 'components/ClaimActions'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockSubmit = jest.fn()
const mockDiscard = jest.fn()
const mockWithdraw = jest.fn()

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
  render(<ClaimActions claim={claim} login="testuser" year="2025" />)

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
      return [jest.fn(), {}]
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
})
