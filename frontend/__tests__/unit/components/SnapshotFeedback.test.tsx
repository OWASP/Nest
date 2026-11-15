import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { signIn } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import SnapshotFeedback, { MAX_COMMENT_LENGTH } from 'components/SnapshotFeedback'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  signIn: jest.fn(),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(),
}))

const SNAPSHOT_KEY = '2024-12'

const feedbackEntry = {
  id: 'feedback-1',
  avatarUrl: 'https://avatars.githubusercontent.com/u/1?v=4',
  comment: 'Really useful digest.',
  createdAt: '2025-01-15T10:00:00.000Z',
  login: 'alice',
  rating: 5,
  updatedAt: '2025-01-15T10:00:00.000Z',
  username: 'alice',
}

describe('SnapshotFeedback', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseMutation = useMutation as unknown as jest.Mock
  const mockAddToast = addToast as jest.Mock
  const mockRefetch = jest.fn()
  const mockSubmit = jest.fn()
  const mockDelete = jest.fn()

  const setupMocks = ({
    session = 'authenticated',
    snapshot = {
      id: 'snapshot-1',
      averageRating: 0,
      feedbackCount: 0,
      myFeedback: null as typeof feedbackEntry | null,
      feedback: [] as (typeof feedbackEntry)[],
    },
    submitResult = {
      data: { submitSnapshotFeedback: { ok: true, message: 'Thanks for your feedback!' } },
    },
    deleteResult = {
      data: { deleteSnapshotFeedback: { ok: true, message: 'Feedback removed successfully.' } },
    },
    loading = false,
    isSyncing = false,
  } = {}) => {
    ;(useDjangoSession as jest.Mock).mockReturnValue({
      isSyncing,
      session: { user: { name: 'testuser' } },
      status: session,
    })

    mockUseQuery.mockReturnValue({
      data: { snapshot },
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    mockSubmit.mockResolvedValue(submitResult)
    mockDelete.mockResolvedValue(deleteResult)

    mockUseMutation.mockImplementation((document, options) => {
      const isSubmit = document?.definitions?.[0]?.name?.value === 'SubmitSnapshotFeedback'
      const trigger = jest.fn(async (vars) => {
        try {
          const result = isSubmit ? await mockSubmit(vars) : await mockDelete(vars)
          options?.onCompleted?.(result.data)
          return result
        } catch (error) {
          options?.onError?.(error)
        }
      })
      return [trigger, { loading }]
    })
  }

  beforeEach(() => jest.clearAllMocks())

  describe('rating summary', () => {
    it('prompts for the first rating when there is no feedback', () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(
        screen.getByText('No ratings yet. Be the first to share your thoughts.')
      ).toBeInTheDocument()
    })

    it('shows the average and a plural count', () => {
      setupMocks({
        snapshot: {
          id: 'snapshot-1',
          averageRating: 4.25,
          feedbackCount: 4,
          myFeedback: null,
          feedback: [feedbackEntry],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText('4.3')).toBeInTheDocument()
      expect(screen.getByText('(4 ratings)')).toBeInTheDocument()
    })

    it('uses the singular form for one rating', () => {
      setupMocks({
        snapshot: {
          id: 'snapshot-1',
          averageRating: 5,
          feedbackCount: 1,
          myFeedback: null,
          feedback: [feedbackEntry],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText('(1 rating)')).toBeInTheDocument()
    })

    it('falls back to zero when the snapshot is missing', () => {
      setupMocks()
      mockUseQuery.mockReturnValue({
        data: null,
        loading: false,
        error: null,
        refetch: mockRefetch,
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(
        screen.getByText('No ratings yet. Be the first to share your thoughts.')
      ).toBeInTheDocument()
    })
  })

  describe('session syncing', () => {
    it('holds the query until the Django session is established', () => {
      setupMocks({ isSyncing: true })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(mockUseQuery).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({ skip: true })
      )
    })

    it('runs the query once the session has settled', () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(mockUseQuery).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({ skip: false })
      )
    })
  })

  describe('unauthenticated visitors', () => {
    it('shows a sign-in prompt instead of the form', () => {
      setupMocks({ session: 'unauthenticated' })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument()
      expect(screen.queryByRole('group', { name: 'Your rating' })).not.toBeInTheDocument()
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    })

    it('triggers GitHub sign-in when the prompt is clicked', () => {
      setupMocks({ session: 'unauthenticated' })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))

      expect(signIn).toHaveBeenCalledWith('github')
    })

    it('still shows existing feedback entries', () => {
      setupMocks({
        session: 'unauthenticated',
        snapshot: {
          id: 'snapshot-1',
          averageRating: 5,
          feedbackCount: 1,
          myFeedback: null,
          feedback: [feedbackEntry],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText('Really useful digest.')).toBeInTheDocument()
      expect(screen.getByText('alice')).toBeInTheDocument()
    })
  })

  describe('submitting new feedback', () => {
    it('renders the empty form for a first-time rater', () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText('Rate this snapshot')).toBeInTheDocument()
      expect(screen.getByText('Submit Feedback')).toBeInTheDocument()
      expect(screen.queryByText('Remove')).not.toBeInTheDocument()
      expect(screen.getByRole('textbox')).toHaveValue('')
    })

    it('warns when submitting without a rating', () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByText('Submit Feedback'))

      expect(mockAddToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Rating required', color: 'warning' })
      )
      expect(mockSubmit).not.toHaveBeenCalled()
    })

    it('submits the selected rating and comment', async () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByRole('button', { name: '4 stars' }))
      fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Great work' } })
      fireEvent.click(screen.getByText('Submit Feedback'))

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith({
          variables: {
            inputData: { snapshotKey: SNAPSHOT_KEY, rating: 4, comment: 'Great work' },
          },
        })
      })
    })

    it('submits without a comment', async () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByRole('button', { name: '3 stars' }))
      fireEvent.click(screen.getByText('Submit Feedback'))

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith({
          variables: { inputData: { snapshotKey: SNAPSHOT_KEY, rating: 3, comment: '' } },
        })
      })
    })

    it('toasts success and refetches on success', async () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByRole('button', { name: '5 stars' }))
      fireEvent.click(screen.getByText('Submit Feedback'))

      await waitFor(() => {
        expect(mockAddToast).toHaveBeenCalledWith(
          expect.objectContaining({ title: 'Thank you!', color: 'success' })
        )
      })
      expect(mockRefetch).toHaveBeenCalled()
    })

    it('surfaces a rejection from the server without refetching', async () => {
      setupMocks({
        submitResult: {
          data: { submitSnapshotFeedback: { ok: false, message: 'Snapshot not found.' } },
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByRole('button', { name: '2 stars' }))
      fireEvent.click(screen.getByText('Submit Feedback'))

      await waitFor(() => {
        expect(mockAddToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            description: 'Snapshot not found.',
            color: 'danger',
          })
        )
      })
      expect(mockRefetch).not.toHaveBeenCalled()
    })

    it('caps the comment at the backend limit', () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByRole('textbox')).toHaveAttribute('maxlength', String(MAX_COMMENT_LENGTH))
    })

    it('tracks the comment length', () => {
      setupMocks()
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText(`0/${MAX_COMMENT_LENGTH}`)).toBeInTheDocument()

      fireEvent.change(screen.getByRole('textbox'), { target: { value: 'abcde' } })

      expect(screen.getByText(`5/${MAX_COMMENT_LENGTH}`)).toBeInTheDocument()
    })
  })

  describe('editing existing feedback', () => {
    const withMyFeedback = {
      id: 'snapshot-1',
      averageRating: 5,
      feedbackCount: 1,
      myFeedback: feedbackEntry,
      feedback: [feedbackEntry],
    }

    it('pre-fills the form from saved feedback', () => {
      setupMocks({ snapshot: withMyFeedback })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText('Update your feedback')).toBeInTheDocument()
      expect(screen.getByRole('textbox')).toHaveValue('Really useful digest.')
      expect(screen.getByRole('button', { name: '5 stars' })).toHaveAttribute(
        'aria-pressed',
        'true'
      )
    })

    it('offers update and remove actions', () => {
      setupMocks({ snapshot: withMyFeedback })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText('Update Feedback')).toBeInTheDocument()
      expect(screen.getByText('Remove')).toBeInTheDocument()
    })

    it('submits a changed rating', async () => {
      setupMocks({ snapshot: withMyFeedback })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByRole('button', { name: '2 stars' }))
      fireEvent.click(screen.getByText('Update Feedback'))

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith({
          variables: {
            inputData: {
              snapshotKey: SNAPSHOT_KEY,
              rating: 2,
              comment: 'Really useful digest.',
            },
          },
        })
      })
    })

    it('deletes the feedback and clears the form', async () => {
      setupMocks({ snapshot: withMyFeedback })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(mockDelete).toHaveBeenCalledWith({ variables: { snapshotKey: SNAPSHOT_KEY } })
      })
      expect(mockAddToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Removed', color: 'success' })
      )
      expect(mockRefetch).toHaveBeenCalled()
    })

    it('surfaces a failed delete', async () => {
      setupMocks({
        snapshot: withMyFeedback,
        deleteResult: {
          data: { deleteSnapshotFeedback: { ok: false, message: 'Feedback not found.' } },
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(mockAddToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            description: 'Feedback not found.',
            color: 'danger',
          })
        )
      })
      expect(mockRefetch).not.toHaveBeenCalled()
    })
  })

  describe('in-flight state', () => {
    it('disables the form while a mutation runs', () => {
      setupMocks({ loading: true })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByText('Saving...')).toBeInTheDocument()
      expect(screen.getByRole('textbox')).toBeDisabled()
      expect(screen.getByRole('button', { name: '3 stars' })).toBeDisabled()
    })
  })

  describe('feedback entries', () => {
    it('lists every entry with its author and comment', () => {
      const second = {
        ...feedbackEntry,
        id: 'feedback-2',
        comment: 'Helpful summary.',
        rating: 4,
        username: 'bob',
      }
      setupMocks({
        snapshot: {
          id: 'snapshot-1',
          averageRating: 4.5,
          feedbackCount: 2,
          myFeedback: null,
          feedback: [feedbackEntry, second],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getAllByTestId('snapshot-feedback-entry')).toHaveLength(2)
      expect(screen.getByText('Really useful digest.')).toBeInTheDocument()
      expect(screen.getByText('Helpful summary.')).toBeInTheDocument()
      expect(screen.getByText('bob')).toBeInTheDocument()
    })

    it("renders the author's GitHub avatar", () => {
      setupMocks({
        snapshot: {
          id: 'snapshot-1',
          averageRating: 5,
          feedbackCount: 1,
          myFeedback: null,
          feedback: [feedbackEntry],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByAltText("alice's avatar")).toHaveAttribute('src', feedbackEntry.avatarUrl)
    })

    it('links the avatar to the author profile', () => {
      setupMocks({
        snapshot: {
          id: 'snapshot-1',
          averageRating: 5,
          feedbackCount: 1,
          myFeedback: null,
          feedback: [feedbackEntry],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByAltText("alice's avatar").closest('a')).toHaveAttribute(
        'href',
        '/members/alice'
      )
    })

    it('falls back to a placeholder avatar when no GitHub account is linked', () => {
      setupMocks({
        snapshot: {
          id: 'snapshot-1',
          averageRating: 5,
          feedbackCount: 1,
          myFeedback: null,
          feedback: [{ ...feedbackEntry, avatarUrl: '', login: '' }],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.queryByAltText("alice's avatar")).not.toBeInTheDocument()
      expect(screen.getByText('alice')).toBeInTheDocument()
    })

    it('renders a rating-only entry without a comment paragraph', () => {
      setupMocks({
        snapshot: {
          id: 'snapshot-1',
          averageRating: 3,
          feedbackCount: 1,
          myFeedback: null,
          feedback: [{ ...feedbackEntry, comment: '', rating: 3 }],
        },
      })
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      expect(screen.getByTestId('snapshot-feedback-entry')).toBeInTheDocument()
      expect(screen.queryByText('Really useful digest.')).not.toBeInTheDocument()
    })
  })

  describe('mutation error handling', () => {
    it('shows a danger toast when submit fails with a network error', async () => {
      setupMocks()
      mockSubmit.mockRejectedValue(new Error('Network error'))
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByRole('button', { name: '4 stars' }))
      fireEvent.click(screen.getByText('Submit Feedback'))

      await waitFor(() => {
        expect(mockAddToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            description: 'Failed to submit your feedback.',
            color: 'danger',
          })
        )
      })
      expect(mockRefetch).not.toHaveBeenCalled()
    })

    it('shows a danger toast when delete fails with a network error', async () => {
      const withMyFeedback = {
        id: 'snapshot-1',
        averageRating: 5,
        feedbackCount: 1,
        myFeedback: feedbackEntry,
        feedback: [feedbackEntry],
      }
      setupMocks({ snapshot: withMyFeedback })
      mockDelete.mockRejectedValue(new Error('Network error'))
      render(<SnapshotFeedback snapshotKey={SNAPSHOT_KEY} />)

      fireEvent.click(screen.getByText('Remove'))

      await waitFor(() => {
        expect(mockAddToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            description: 'Failed to remove your feedback.',
            color: 'danger',
          })
        )
      })
      expect(mockRefetch).not.toHaveBeenCalled()
    })
  })
})
