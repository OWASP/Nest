import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { render } from 'wrappers/testUtil'
import EditEvidencePage from 'app/board/[year]/candidates/[login]/claims/[claimKey]/evidences/[evidenceKey]/edit/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    claimKey: 'experience-leadership',
    evidenceKey: 'certificate',
    login: 'testuser',
    year: '2025',
  })),
  useRouter: jest.fn(() => mockRouter),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title, message }: { title: string; message: string }) => (
    <div data-testid="error-display">
      <span data-testid="error-title">{title}</span>
      <span data-testid="error-message">{message}</span>
    </div>
  ),
}))

const mockRouter = { push: jest.fn() }

const mockUseMutation = useMutation as unknown as jest.Mock
const mockUseQuery = useQuery as unknown as jest.Mock
const mockUpdateFn = jest.fn()
const mockUseDjangoSession = useDjangoSession as jest.Mock
const stableEvidence = {
  boardCandidateClaimEvidence: {
    __typename: 'BoardCandidateClaimEvidenceNode',
    id: 'evidence-1',
    createdAt: '2025-01-16T10:00:00Z',
    description: 'Certificate of completion.',
    hasFile: true,
    key: 'certificate',
    name: 'Certificate',
    sourceUrl: 'https://example.com/cert',
    updatedAt: '2025-01-16T10:00:00Z',
  },
}

describe('EditEvidencePage', () => {
  beforeEach(() => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'testuser' } },
      status: 'authenticated',
    })
    mockUpdateFn.mockResolvedValue({
      data: {
        updateBoardCandidateClaimEvidence: {
          ok: true,
          code: null,
          message: null,
          evidence: {
            __typename: 'BoardCandidateClaimEvidenceNode',
            id: 'evidence-1',
            createdAt: '2025-01-16T10:00:00Z',
            description: 'Updated description',
            hasFile: true,
            key: 'certificate',
            name: 'Updated Certificate',
            sourceUrl: 'https://example.com/updated',
            updatedAt: '2025-01-17T10:00:00Z',
          },
        },
      },
    })
    mockUseMutation.mockReturnValue([mockUpdateFn, { loading: false }])
    mockUseQuery.mockReturnValue({ data: stableEvidence, loading: false, error: null })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when query is loading', () => {
    mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

    render(<EditEvidencePage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders 404 when evidence is not found', async () => {
    mockUseQuery.mockReturnValue({
      data: { boardCandidateClaimEvidence: null },
      loading: false,
      error: null,
    })

    render(<EditEvidencePage />)

    await waitFor(() => {
      expect(screen.getByTestId('error-display')).toBeInTheDocument()
    })
    expect(screen.getByTestId('error-title')).toHaveTextContent('Evidence Not Found')
  })

  test('renders access denied when viewing another user profile', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'otheruser' } },
      status: 'authenticated',
    })

    render(<EditEvidencePage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders form pre-filled with existing evidence data', async () => {
    render(<EditEvidencePage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Certificate')).toBeInTheDocument()
    })
    expect(screen.getByDisplayValue('Certificate of completion.')).toBeInTheDocument()
    expect(screen.getByDisplayValue('https://example.com/cert')).toBeInTheDocument()
  })

  test('submits form and redirects on success', async () => {
    render(<EditEvidencePage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Certificate')).toBeInTheDocument()
    })

    await userEvent.clear(screen.getByPlaceholderText('Enter evidence name'))
    await userEvent.type(screen.getByPlaceholderText('Enter evidence name'), 'Updated Certificate')
    await userEvent.type(
      screen.getByPlaceholderText('Enter evidence description'),
      ' Updated description'
    )

    await userEvent.click(screen.getByRole('button', { name: /update evidence/i }))

    await waitFor(() => {
      expect(mockUpdateFn).toHaveBeenCalled()
    })
    expect(mockRouter.push).toHaveBeenCalledWith(
      '/board/2025/candidates/testuser/claims/experience-leadership/evidences/certificate'
    )
  })

  test('shows error toast on mutation failure', async () => {
    mockUpdateFn.mockRejectedValue(new Error('Update failed'))

    render(<EditEvidencePage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Certificate')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /update evidence/i }))

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Update failed',
          color: 'danger',
        })
      )
    })
  })

  test('does not submit when validation fails', async () => {
    render(<EditEvidencePage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Certificate')).toBeInTheDocument()
    })

    await userEvent.clear(screen.getByPlaceholderText('Enter evidence name'))
    await userEvent.clear(screen.getByPlaceholderText('Enter evidence description'))

    await userEvent.click(screen.getByRole('button', { name: /update evidence/i }))

    expect(mockUpdateFn).not.toHaveBeenCalled()
  })

  test('shows backend validation errors from GraphQL', async () => {
    const gqlError = {
      graphQLErrors: [
        {
          message: 'Name is required',
          extensions: { code: 'VALIDATION_ERROR', field: 'name' },
        },
      ],
    }
    mockUpdateFn.mockRejectedValue(gqlError)

    render(<EditEvidencePage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Certificate')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /update evidence/i }))

    await waitFor(() => {
      expect(mockUpdateFn).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument()
    })
  })

  test('clears backend error when user types after validation error', async () => {
    const gqlError = {
      graphQLErrors: [
        {
          message: 'Name is required',
          extensions: { code: 'VALIDATION_ERROR', field: 'name' },
        },
      ],
    }
    mockUpdateFn.mockRejectedValue(gqlError)

    render(<EditEvidencePage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Certificate')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /update evidence/i }))

    await waitFor(() => {
      expect(mockUpdateFn).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter evidence name'), ' Updated Name')

    expect(screen.getByPlaceholderText('Enter evidence name')).toHaveValue(
      'Certificate Updated Name'
    )

    await waitFor(() => {
      expect(screen.queryByText('Name is required')).not.toBeInTheDocument()
    })
  })
})
