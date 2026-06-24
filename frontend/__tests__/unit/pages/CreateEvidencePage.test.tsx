import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { render } from 'wrappers/testUtil'
import CreateEvidencePage from 'app/board/[year]/candidates/[login]/claims/[claimKey]/evidences/create/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: jest.fn(),
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

const mockRouter = { push: jest.fn() }

const mockUseMutation = useMutation as unknown as jest.Mock
const mockCreateFn = jest.fn()
const mockUseDjangoSession = useDjangoSession as jest.Mock

describe('CreateEvidencePage', () => {
  beforeEach(() => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'testuser' } },
      status: 'authenticated',
    })
    mockCreateFn.mockResolvedValue({
      data: {
        createBoardCandidateClaimEvidence: {
          ok: true,
          code: null,
          message: null,
          evidence: {
            __typename: 'BoardCandidateClaimEvidenceNode',
            id: 'new-evidence',
            key: 'new-evidence',
            name: 'New Evidence',
            description: 'New description',
            sourceUrl: 'https://example.com/doc',
            hasFile: false,
            createdAt: '2025-01-16T10:00:00Z',
            updatedAt: '2025-01-16T10:00:00Z',
          },
        },
      },
    })
    mockUseMutation.mockReturnValue([mockCreateFn, { loading: false }])
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when session is syncing', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: true,
      session: null,
      status: 'loading',
    })

    render(<CreateEvidencePage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders access denied when viewing another user profile', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'otheruser' } },
      status: 'authenticated',
    })

    render(<CreateEvidencePage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders evidence form with name, description, source URL, and file fields', async () => {
    render(<CreateEvidencePage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter evidence name')).toBeInTheDocument()
    })
    expect(screen.getByPlaceholderText('Enter evidence description')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('https://example.com/document.pdf')).toBeInTheDocument()
  })

  test('submits form and redirects on success', async () => {
    render(<CreateEvidencePage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter evidence name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter evidence name'), 'New Evidence')
    await userEvent.type(
      screen.getByPlaceholderText('Enter evidence description'),
      'New description'
    )
    await userEvent.type(
      screen.getByPlaceholderText('https://example.com/document.pdf'),
      'https://example.com/doc'
    )

    await userEvent.click(screen.getByRole('button', { name: /add evidence/i }))

    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalled()
    })
    expect(mockRouter.push).toHaveBeenCalledWith(
      '/board/2025/candidates/testuser/claims/experience-leadership'
    )
  })

  test('shows error toast on mutation failure', async () => {
    mockCreateFn.mockRejectedValue(new Error('Creation failed'))

    render(<CreateEvidencePage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter evidence name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter evidence name'), 'New Evidence')
    await userEvent.type(
      screen.getByPlaceholderText('Enter evidence description'),
      'New description'
    )
    await userEvent.type(
      screen.getByPlaceholderText('https://example.com/document.pdf'),
      'https://example.com/doc'
    )
    await userEvent.click(screen.getByRole('button', { name: /add evidence/i }))

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
    render(<CreateEvidencePage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter evidence name')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole('button', { name: /add evidence/i }))

    expect(mockCreateFn).not.toHaveBeenCalled()
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
    mockCreateFn.mockRejectedValue(gqlError)

    render(<CreateEvidencePage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter evidence name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter evidence name'), 'New Evidence')
    await userEvent.type(
      screen.getByPlaceholderText('Enter evidence description'),
      'New description'
    )
    await userEvent.type(
      screen.getByPlaceholderText('https://example.com/document.pdf'),
      'https://example.com/doc'
    )
    await userEvent.click(screen.getByRole('button', { name: /add evidence/i }))

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
        {
          message: 'Name is required',
          extensions: { code: 'VALIDATION_ERROR', field: 'name' },
        },
      ],
    }
    mockCreateFn.mockRejectedValue(gqlError)

    render(<CreateEvidencePage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter evidence name')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter evidence name'), 'New Evidence')
    await userEvent.type(
      screen.getByPlaceholderText('Enter evidence description'),
      'New description'
    )
    await userEvent.type(
      screen.getByPlaceholderText('https://example.com/document.pdf'),
      'https://example.com/doc'
    )
    await userEvent.click(screen.getByRole('button', { name: /add evidence/i }))

    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByPlaceholderText('Enter evidence name'), ' Updated Name')

    expect(screen.getByPlaceholderText('Enter evidence name')).toHaveValue(
      'New Evidence Updated Name'
    )

    await waitFor(() => {
      expect(screen.queryByText('Name is required')).not.toBeInTheDocument()
    })
  })
})
