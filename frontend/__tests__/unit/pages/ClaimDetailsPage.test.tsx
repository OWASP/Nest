import { useQuery } from '@apollo/client/react'
import { mockSingleClaim, mockEvidences } from '@mockData/mockClaimData'
import { screen, waitFor } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { render } from 'wrappers/testUtil'
import ClaimDetailsPage from 'app/board/[year]/candidates/[login]/claims/[claimKey]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    claimKey: 'experience-leadership',
    login: 'testuser',
    year: '2025',
  })),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
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

jest.mock('components/ClaimActions', () => ({
  __esModule: true,
  default: () => <div data-testid="claim-actions" />,
}))

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseDjangoSession = useDjangoSession as jest.Mock
const stableData = {
  boardCandidateClaim: mockSingleClaim,
  boardCandidateClaimEvidences: mockEvidences,
}

describe('ClaimDetailsPage', () => {
  beforeEach(() => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'testuser' } },
      status: 'authenticated',
    })
    mockUseQuery.mockReturnValue({ data: stableData, loading: false, error: null })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when query is loading', () => {
    mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

    render(<ClaimDetailsPage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders 404 when claim is not found', async () => {
    mockUseQuery.mockReturnValue({
      data: { boardCandidateClaim: null, boardCandidateClaimEvidences: [] },
      loading: false,
      error: null,
    })

    render(<ClaimDetailsPage />)

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

    render(<ClaimDetailsPage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders claim name in claim details metadata', async () => {
    render(<ClaimDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText(/Leadership Experience/i)).toBeInTheDocument()
    })
    expect(screen.getByText('Claim Details')).toBeInTheDocument()
  })

  test('renders evidence list with evidence items', async () => {
    render(<ClaimDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Evidences')).toBeInTheDocument()
    })
    expect(screen.getByText('Certificate')).toBeInTheDocument()
    expect(screen.getByText('Reference Letter')).toBeInTheDocument()
  })

  test('renders add evidence button for draft claims', async () => {
    render(<ClaimDetailsPage />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add evidence/i })).toBeInTheDocument()
    })
  })

  test('renders empty state when no evidences exist', async () => {
    mockUseQuery.mockReturnValue({
      data: { boardCandidateClaim: mockSingleClaim, boardCandidateClaimEvidences: [] },
      loading: false,
      error: null,
    })

    render(<ClaimDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('No evidences.')).toBeInTheDocument()
    })
  })

  test('renders ClaimActions component', async () => {
    render(<ClaimDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('claim-actions')).toBeInTheDocument()
    })
  })

  const NON_OWNER = { user: { login: 'otheruser' } }
  const ANONYMOUS = null

  const setupAccessCase = (status: string, session: { user: { login: string } } | null): void => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session,
      status: session ? 'authenticated' : 'unauthenticated',
    })
    mockUseQuery.mockReturnValue({
      data: {
        boardCandidateClaim: { ...mockSingleClaim, status },
        boardCandidateClaimEvidences: mockEvidences,
      },
      loading: false,
      error: null,
    })
  }

  test.each([
    ['APPROVED', 'non-owner', NON_OWNER],
    ['APPROVED', 'anonymous', ANONYMOUS],
    ['REJECTED', 'non-owner', NON_OWNER],
    ['REJECTED', 'anonymous', ANONYMOUS],
  ] as const)('%s claim is visible to %s viewer', async (status, _label, session) => {
    setupAccessCase(status, session)
    render(<ClaimDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText(/Leadership Experience/i)).toBeInTheDocument()
    })
  })

  test.each([
    ['SUBMITTED', 'non-owner', NON_OWNER],
    ['SUBMITTED', 'anonymous', ANONYMOUS],
    ['DRAFT', 'non-owner', NON_OWNER],
    ['DRAFT', 'anonymous', ANONYMOUS],
  ] as const)('%s claim is denied for %s viewer', (status, _label, session) => {
    setupAccessCase(status, session)
    render(<ClaimDetailsPage />)
    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('does not render ClaimActions for non-owner, non-reviewer public viewer', async () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'otheruser' } },
      status: 'authenticated',
    })
    mockUseQuery.mockReturnValue({
      data: {
        boardCandidateClaim: { ...mockSingleClaim, status: 'APPROVED' },
        boardCandidateClaimEvidences: mockEvidences,
      },
      loading: false,
      error: null,
    })

    render(<ClaimDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText(/Leadership Experience/i)).toBeInTheDocument()
    })
    expect(screen.queryByTestId('claim-actions')).not.toBeInTheDocument()
  })
})
