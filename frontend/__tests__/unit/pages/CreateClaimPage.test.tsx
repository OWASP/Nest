import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { render } from 'wrappers/testUtil'
import CreateClaimPage from 'app/board/[year]/candidates/[login]/claims/create/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ login: 'testuser', year: '2025' })),
  useRouter: jest.fn(() => mockRouter),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRouter = { push: jest.fn() }

const mockUseMutation = useMutation as unknown as jest.Mock
const mockUseQuery = useQuery as unknown as jest.Mock
const mockCreateFn = jest.fn()
const mockUseDjangoSession = useDjangoSession as jest.Mock

describe('CreateClaimPage', () => {
  beforeEach(() => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'testuser' } },
      status: 'authenticated',
    })
    mockCreateFn.mockResolvedValue({
      data: {
        createBoardCandidateClaim: {
          ok: true,
          code: null,
          message: null,
          claim: {
            __typename: 'BoardCandidateClaimNode',
            id: 'new-claim',
            key: 'new-claim',
            name: 'New Claim',
            description: 'New description',
            status: 'DRAFT',
            order: 1,
            createdAt: '2025-01-15T10:00:00Z',
            updatedAt: '2025-01-15T10:00:00Z',
          },
        },
      },
    })
    mockUseMutation.mockReturnValue([mockCreateFn, { loading: false }])
    mockUseQuery.mockReturnValue({
      data: {
        boardOfDirectors: {
          candidate: { id: 'candidate-1' },
        },
      },
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when query is loading', () => {
    mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

    render(<CreateClaimPage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders error display when candidate query fails', () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error('Network error'),
    })

    render(<CreateClaimPage />)

    expect(screen.getByText('Error loading candidate')).toBeInTheDocument()
    expect(
      screen.getByText('An error occurred while loading the candidate data')
    ).toBeInTheDocument()
  })

  test('renders access denied when user is not a candidate', () => {
    mockUseQuery.mockReturnValue({
      data: { boardOfDirectors: { candidate: null } },
      loading: false,
      error: null,
    })

    render(<CreateClaimPage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders access denied when viewing another user profile', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'otheruser' } },
      status: 'authenticated',
    })

    render(<CreateClaimPage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders claim form with name and description fields', async () => {
    render(<CreateClaimPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter claim name')).toBeInTheDocument()
    })
    expect(screen.getByPlaceholderText('Enter claim description')).toBeInTheDocument()
  })

  test('submits form and redirects on success', async () => {
    render(<CreateClaimPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter claim name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter claim name'), 'New Claim')
    await userEvent.type(screen.getByPlaceholderText('Enter claim description'), 'New description')

    await userEvent.click(screen.getByRole('button', { name: /create claim/i }))

    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalled()
    })
    expect(mockRouter.push).toHaveBeenCalledWith('/board/2025/candidates/testuser/claims')
  })

  test('shows error toast on mutation failure', async () => {
    mockCreateFn.mockRejectedValue(new Error('Creation failed'))

    render(<CreateClaimPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter claim name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter claim name'), 'New Claim')
    await userEvent.type(screen.getByPlaceholderText('Enter claim description'), 'New description')
    await userEvent.click(screen.getByRole('button', { name: /create claim/i }))

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Creation failed',
          color: 'danger',
        })
      )
    })
  })

  test('does not submit when validation fails', async () => {
    render(<CreateClaimPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter claim name')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /create claim/i }))

    expect(mockCreateFn).not.toHaveBeenCalled()
  })

  test('shows backend validation errors from GraphQL', async () => {
    const gqlError = {
      graphQLErrors: [
        { message: 'Name is required', extensions: { code: 'VALIDATION_ERROR', field: 'name' } },
      ],
    }
    mockCreateFn.mockRejectedValue(gqlError)

    render(<CreateClaimPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter claim name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter claim name'), 'New Claim')
    await userEvent.type(screen.getByPlaceholderText('Enter claim description'), 'New description')
    await userEvent.click(screen.getByRole('button', { name: /create claim/i }))

    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument()
    })
  })

  test('clears backend error when user types after validation error', async () => {
    const gqlError = {
      graphQLErrors: [
        { message: 'Name is required', extensions: { code: 'VALIDATION_ERROR', field: 'name' } },
      ],
    }
    mockCreateFn.mockRejectedValue(gqlError)

    render(<CreateClaimPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter claim name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter claim name'), 'New Claim')
    await userEvent.type(screen.getByPlaceholderText('Enter claim description'), 'New description')
    await userEvent.click(screen.getByRole('button', { name: /create claim/i }))

    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter claim name'), ' Updated Name')

    expect(screen.getByPlaceholderText('Enter claim name')).toHaveValue('New Claim Updated Name')

    await waitFor(() => {
      expect(screen.queryByText('Name is required')).not.toBeInTheDocument()
    })
  })
})
