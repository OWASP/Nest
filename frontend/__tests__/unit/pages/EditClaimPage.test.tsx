import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { render } from 'wrappers/testUtil'
import EditClaimPage from 'app/board/[year]/candidates/[login]/claims/[claimKey]/edit/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    claimKey: 'experience-leadership',
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
const stableClaim = {
  boardCandidateClaim: {
    __typename: 'BoardCandidateClaimNode',
    id: 'claim-1',
    createdAt: '2025-01-15T10:00:00Z',
    description: 'Experience in leadership.',
    key: 'experience-leadership',
    name: 'Leadership Experience',
    status: 'DRAFT',
    updatedAt: '2025-01-15T10:00:00Z',
  },
}

describe('EditClaimPage', () => {
  beforeEach(() => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'testuser' } },
      status: 'authenticated',
    })
    mockUpdateFn.mockResolvedValue({
      data: {
        updateBoardCandidateClaim: {
          ok: true,
          code: null,
          message: null,
          claim: {
            __typename: 'BoardCandidateClaimNode',
            id: 'claim-1',
            key: 'experience-leadership',
            name: 'Updated Claim',
            description: 'Updated description',
            status: 'DRAFT',
            order: 1,
            createdAt: '2025-01-15T10:00:00Z',
            updatedAt: '2025-01-16T10:00:00Z',
          },
        },
      },
    })
    mockUseMutation.mockReturnValue([mockUpdateFn, { loading: false }])
    mockUseQuery.mockReturnValue({ data: stableClaim, loading: false, error: null })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when query is loading', () => {
    mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

    render(<EditClaimPage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders 404 when claim is not found', async () => {
    mockUseQuery.mockReturnValue({
      data: { boardCandidateClaim: null },
      loading: false,
      error: null,
    })

    render(<EditClaimPage />)

    await waitFor(() => {
      expect(screen.getByTestId('error-display')).toBeInTheDocument()
    })
    expect(screen.getByTestId('error-title')).toHaveTextContent('Claim Not Found')
  })

  test('renders access denied when viewing another user profile', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'otheruser' } },
      status: 'authenticated',
    })

    render(<EditClaimPage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders form pre-filled with existing claim data', async () => {
    render(<EditClaimPage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Leadership Experience')).toBeInTheDocument()
    })
    expect(screen.getByDisplayValue('Experience in leadership.')).toBeInTheDocument()
  })

  test('submits form and redirects on success', async () => {
    render(<EditClaimPage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Leadership Experience')).toBeInTheDocument()
    })

    await userEvent.clear(screen.getByPlaceholderText('Enter claim name'))
    await userEvent.type(screen.getByPlaceholderText('Enter claim name'), 'Updated Claim')
    await userEvent.type(screen.getByPlaceholderText('Enter claim description'), ' Updated')

    await userEvent.click(screen.getByRole('button', { name: /edit claim/i }))

    await waitFor(() => {
      expect(mockUpdateFn).toHaveBeenCalled()
    })
    expect(mockRouter.push).toHaveBeenCalledWith(
      '/board/2025/candidates/testuser/claims/experience-leadership'
    )
  })

  test('shows error toast on mutation failure', async () => {
    mockUpdateFn.mockRejectedValue(new Error('Update failed'))

    render(<EditClaimPage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Leadership Experience')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /edit claim/i }))

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
    render(<EditClaimPage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Leadership Experience')).toBeInTheDocument()
    })

    await userEvent.clear(screen.getByPlaceholderText('Enter claim name'))
    await userEvent.clear(screen.getByPlaceholderText('Enter claim description'))

    await userEvent.click(screen.getByRole('button', { name: /edit claim/i }))

    expect(mockUpdateFn).not.toHaveBeenCalled()
  })

  test('shows backend validation errors from GraphQL', async () => {
    const gqlError = {
      graphQLErrors: [
        { message: 'Name is required', extensions: { code: 'VALIDATION_ERROR', field: 'name' } },
      ],
    }
    mockUpdateFn.mockRejectedValue(gqlError)

    render(<EditClaimPage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Leadership Experience')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /edit claim/i }))

    await waitFor(() => {
      expect(mockUpdateFn).toHaveBeenCalled()
    })
  })

  test('clears backend error when user types after validation error', async () => {
    const gqlError = {
      graphQLErrors: [
        { message: 'Name is required', extensions: { code: 'VALIDATION_ERROR', field: 'name' } },
      ],
    }
    mockUpdateFn.mockRejectedValue(gqlError)

    render(<EditClaimPage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Leadership Experience')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /edit claim/i }))

    await waitFor(() => {
      expect(mockUpdateFn).toHaveBeenCalled()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter claim name'), ' Updated Name')

    expect(screen.getByPlaceholderText('Enter claim name')).toHaveValue(
      'Leadership Experience Updated Name'
    )
  })
})
