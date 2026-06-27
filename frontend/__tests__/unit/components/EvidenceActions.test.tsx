import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { GetClaimAndEvidencesDocument } from 'types/__generated__/claimQueries.generated'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
import EvidenceActions from 'components/EvidenceActions'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRemove = jest.fn()

const baseClaim = {
  id: 'claim-1',
  key: 'test-claim',
  name: 'Test Claim',
  description: 'Test description',
  status: ClaimStatusEnum.Draft,
  updatedAt: '2025-01-15T10:00:00Z',
}

const baseEvidence = {
  id: 'evidence-1',
  key: 'test-evidence',
  name: 'Test Evidence',
  description: 'Test evidence description',
  sourceUrl: 'https://example.com/test',
  createdAt: '2025-01-16T10:00:00Z',
  updatedAt: '2025-01-16T10:00:00Z',
}

const renderEvidenceActions = (
  claim: typeof baseClaim = baseClaim,
  evidence: typeof baseEvidence = baseEvidence
) => render(<EvidenceActions claim={claim} evidence={evidence} login="testuser" year="2025" />)

const openDropdown = (label: string) => {
  fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
  fireEvent.click(screen.getByText(label))
}

describe('EvidenceActions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockRemove, {}])
  })

  describe('renders correct options per claim status', () => {
    it('shows edit and remove for DRAFT', () => {
      renderEvidenceActions()

      const button = screen.getByRole('button', { name: /actions menu/i })
      expect(button).toBeInTheDocument()

      fireEvent.click(button)
      expect(screen.getByText('Edit Evidence')).toBeInTheDocument()
      expect(screen.getByText('Remove Evidence')).toBeInTheDocument()
    })

    it('shows only remove for DISCARDED', () => {
      renderEvidenceActions({ ...baseClaim, status: ClaimStatusEnum.Discarded })

      fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
      expect(screen.getByText('Remove Evidence')).toBeInTheDocument()
      expect(screen.queryByText('Edit Evidence')).not.toBeInTheDocument()
    })

    it('shows only remove for WITHDRAWN', () => {
      renderEvidenceActions({ ...baseClaim, status: ClaimStatusEnum.Withdrawn })

      fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))
      expect(screen.getByText('Remove Evidence')).toBeInTheDocument()
      expect(screen.queryByText('Edit Evidence')).not.toBeInTheDocument()
    })

    it('shows no dropdown items for SUBMITTED', () => {
      renderEvidenceActions({ ...baseClaim, status: ClaimStatusEnum.Submitted })
      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
      expect(screen.queryByText('Edit Evidence')).not.toBeInTheDocument()
      expect(screen.queryByText('Remove Evidence')).not.toBeInTheDocument()
    })

    it('shows no dropdown items for APPROVED', () => {
      renderEvidenceActions({ ...baseClaim, status: ClaimStatusEnum.Approved })
      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
      expect(screen.queryByText('Edit Evidence')).not.toBeInTheDocument()
      expect(screen.queryByText('Remove Evidence')).not.toBeInTheDocument()
    })

    it('shows no dropdown items for REJECTED', () => {
      renderEvidenceActions({ ...baseClaim, status: ClaimStatusEnum.Rejected })
      expect(screen.queryByRole('button', { name: /actions menu/i })).not.toBeInTheDocument()
      expect(screen.queryByText('Edit Evidence')).not.toBeInTheDocument()
      expect(screen.queryByText('Remove Evidence')).not.toBeInTheDocument()
    })
  })

  describe('remove action', () => {
    it('removes evidence and navigates on success', async () => {
      const mockPush = (useRouter as jest.Mock)().push
      const mockCache = { readQuery: jest.fn(), writeQuery: jest.fn() }
      mockRemove.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: {
              removeBoardCandidateClaimEvidence: {
                ok: true,
                evidence: null,
              },
            },
          })
        return Promise.resolve({
          data: {
            removeBoardCandidateClaimEvidence: { ok: true, evidence: null },
          },
        })
      })

      renderEvidenceActions()
      openDropdown('Remove Evidence')

      expect(screen.getByText(/Are you sure/i)).toBeInTheDocument()
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(mockRemove).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: {
              input: {
                key: 'test-evidence',
                claimKey: 'test-claim',
                removedReason: null,
                year: 2025,
              },
            },
          })
        )
      })
      expect(mockPush).toHaveBeenCalledWith('/board/2025/candidates/testuser/claims/test-claim')
    })

    it('removes evidence with reason and navigates on success', async () => {
      mockRemove.mockResolvedValue({
        data: {
          removeBoardCandidateClaimEvidence: { ok: true, evidence: null },
        },
      })

      renderEvidenceActions()
      openDropdown('Remove Evidence')

      const textarea = screen.getByLabelText('Reason for removal')
      fireEvent.change(textarea, { target: { value: 'Duplicate' } })
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(mockRemove).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: {
              input: {
                key: 'test-evidence',
                claimKey: 'test-claim',
                removedReason: 'Duplicate',
                year: 2025,
              },
            },
          })
        )
      })
    })

    it('shows error toast when remove returns ok: false', async () => {
      mockRemove.mockResolvedValue({
        data: {
          removeBoardCandidateClaimEvidence: { ok: false, message: 'Cannot remove' },
        },
      })

      renderEvidenceActions()
      openDropdown('Remove Evidence')
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Cannot remove', color: 'danger' })
        )
      })
    })

    it('shows error toast when remove returns ok: false with fallback message', async () => {
      mockRemove.mockResolvedValue({
        data: { removeBoardCandidateClaimEvidence: { ok: false } },
      })

      renderEvidenceActions()
      openDropdown('Remove Evidence')
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Evidence remove failed.', color: 'danger' })
        )
      })
    })

    it('shows error toast on mutation failure', async () => {
      mockRemove.mockRejectedValue(new Error('Network error'))

      renderEvidenceActions()
      openDropdown('Remove Evidence')
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Network error', color: 'danger' })
        )
      })
    })
  })

  describe('edit navigation', () => {
    it('navigates to edit page when Edit Evidence is clicked', () => {
      const mockPush = (useRouter as jest.Mock)().push
      renderEvidenceActions()

      const button = screen.getByRole('button', { name: /actions menu/i })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      fireEvent.click(screen.getByText('Edit Evidence'))
      expect(mockPush).toHaveBeenCalledWith(
        '/board/2025/candidates/testuser/claims/test-claim/evidences/test-evidence/edit'
      )
    })
  })

  describe('modal behavior', () => {
    it('opens modal when Remove Evidence is clicked', () => {
      renderEvidenceActions()
      openDropdown('Remove Evidence')

      expect(screen.getByText(/Are you sure you want to remove/i)).toBeInTheDocument()
    })

    it('closes modal when Cancel is clicked', async () => {
      renderEvidenceActions()
      openDropdown('Remove Evidence')
      expect(screen.getByText(/Are you sure/i)).toBeInTheDocument()

      fireEvent.click(screen.getByText('Cancel'))

      await waitFor(() => {
        expect(screen.queryByText(/Are you sure/i)).not.toBeInTheDocument()
      })
    })

    it('closes modal when X is clicked', async () => {
      renderEvidenceActions()
      openDropdown('Remove Evidence')

      const closeButton = screen.getByRole('button', { name: /close/i })
      fireEvent.click(closeButton)

      await waitFor(() => {
        expect(screen.queryByText(/Are you sure/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('cache update', () => {
    it('filters removed evidence from cache when existing data is present', async () => {
      const mockCache = {
        readQuery: jest.fn().mockReturnValue({
          boardCandidateClaim: { key: 'test-claim', name: 'Test Claim' },
          boardCandidateClaimEvidences: [
            { key: 'test-evidence', name: 'Test Evidence' },
            { key: 'other-evidence', name: 'Other Evidence' },
          ],
        }),
        writeQuery: jest.fn(),
      }

      mockRemove.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: { removeBoardCandidateClaimEvidence: { ok: true, evidence: null } },
          })
        return Promise.resolve({
          data: { removeBoardCandidateClaimEvidence: { ok: true, evidence: null } },
        })
      })

      renderEvidenceActions()
      openDropdown('Remove Evidence')
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(mockCache.readQuery).toHaveBeenCalledWith({
          query: GetClaimAndEvidencesDocument,
          variables: { key: 'test-claim', login: 'testuser', year: 2025 },
        })
        expect(mockCache.writeQuery).toHaveBeenCalledWith(
          expect.objectContaining({
            data: {
              boardCandidateClaim: { key: 'test-claim', name: 'Test Claim' },
              boardCandidateClaimEvidences: [{ key: 'other-evidence', name: 'Other Evidence' }],
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

      mockRemove.mockImplementation(({ update }) => {
        if (update)
          update(mockCache, {
            data: { removeBoardCandidateClaimEvidence: { ok: true, evidence: null } },
          })
        return Promise.resolve({
          data: { removeBoardCandidateClaimEvidence: { ok: true, evidence: null } },
        })
      })

      renderEvidenceActions()
      openDropdown('Remove Evidence')
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(mockCache.readQuery).toHaveBeenCalled()
        expect(mockCache.writeQuery).not.toHaveBeenCalled()
      })
    })
  })

  describe('error handling - non-Error thrown values', () => {
    it('handles non-Error thrown values gracefully', async () => {
      mockRemove.mockRejectedValue('string error')

      renderEvidenceActions()
      openDropdown('Remove Evidence')
      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({ description: 'Evidence remove failed.' })
        )
      })
    })
  })
})
