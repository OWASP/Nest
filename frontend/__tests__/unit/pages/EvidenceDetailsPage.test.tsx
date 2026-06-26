import { useLazyQuery, useQuery } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { render } from 'wrappers/testUtil'
import EvidenceDetailsPage from 'app/board/[year]/candidates/[login]/claims/[claimKey]/evidences/[evidenceKey]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useLazyQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    claimKey: 'experience-leadership',
    evidenceKey: 'certificate',
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

jest.mock('components/EvidenceActions', () => ({
  __esModule: true,
  default: () => <div data-testid="evidence-actions" />,
}))

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseLazyQuery = useLazyQuery as unknown as jest.Mock
const mockUseDjangoSession = useDjangoSession as jest.Mock

const stableData = {
  boardCandidateClaim: {
    __typename: 'BoardCandidateClaimNode',
    id: 'claim-1',
    key: 'experience-leadership',
    name: 'Leadership Experience',
    description: 'Experience in leadership.',
    status: 'DRAFT',
    createdAt: '2025-01-15T10:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  boardCandidateClaimEvidences: [
    {
      __typename: 'BoardCandidateClaimEvidenceNode',
      id: 'evidence-1',
      key: 'certificate',
      name: 'Certificate',
      description: 'Certificate of completion.',
      sourceUrl: 'https://example.com/cert',
      hasFile: true,
      createdAt: '2025-01-16T10:00:00Z',
      updatedAt: '2025-01-16T10:00:00Z',
    },
    {
      __typename: 'BoardCandidateClaimEvidenceNode',
      id: 'evidence-2',
      key: 'reference-letter',
      name: 'Reference Letter',
      description: 'Reference letter.',
      sourceUrl: 'https://example.com/ref',
      hasFile: false,
      createdAt: '2025-01-17T10:00:00Z',
      updatedAt: '2025-01-17T10:00:00Z',
    },
  ],
}

describe('EvidenceDetailsPage', () => {
  beforeEach(() => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'testuser' } },
      status: 'authenticated',
    })
    mockUseQuery.mockReturnValue({ data: stableData, loading: false, error: null })
    mockUseLazyQuery.mockReturnValue([jest.fn(), { loading: false }])
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when query is loading', () => {
    mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

    render(<EvidenceDetailsPage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders 404 when evidence is not found', async () => {
    mockUseQuery.mockReturnValue({
      data: {
        boardCandidateClaim: stableData.boardCandidateClaim,
        boardCandidateClaimEvidences: [],
      },
      loading: false,
      error: null,
    })

    render(<EvidenceDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('error-display')).toBeInTheDocument()
    })
    expect(screen.getByTestId('error-title')).toHaveTextContent('Evidence Not Found')
  })

  test('renders 404 when claim is not found', async () => {
    mockUseQuery.mockReturnValue({
      data: {
        boardCandidateClaim: null,
        boardCandidateClaimEvidences: stableData.boardCandidateClaimEvidences,
      },
      loading: false,
      error: null,
    })

    render(<EvidenceDetailsPage />)

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

    render(<EvidenceDetailsPage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders evidence details', async () => {
    render(<EvidenceDetailsPage />)

    await waitFor(() => {
      expect(screen.getAllByText(/Certificate/i).length).toBeGreaterThanOrEqual(2)
    })
    expect(screen.getByText('Certificate of completion.')).toBeInTheDocument()
    expect(screen.getByText('https://example.com/cert')).toBeInTheDocument()
    expect(screen.getByText('Evidence Details')).toBeInTheDocument()
  })

  test('renders download button when evidence has file', async () => {
    render(<EvidenceDetailsPage />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /download evidence/i })).toBeInTheDocument()
    })
  })

  test('does not render download button when evidence has no file', async () => {
    mockUseQuery.mockReturnValue({
      data: {
        boardCandidateClaim: stableData.boardCandidateClaim,
        boardCandidateClaimEvidences: [stableData.boardCandidateClaimEvidences[1]],
      },
      loading: false,
      error: null,
    })

    render(<EvidenceDetailsPage />)

    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /download evidence/i })).not.toBeInTheDocument()
    })
  })

  test('renders EvidenceActions component', async () => {
    render(<EvidenceDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('evidence-actions')).toBeInTheDocument()
    })
  })

  test('renders 500 error display on query error', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error('GraphQL error'),
    })

    render(<EvidenceDetailsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('error-display')).toBeInTheDocument()
    })
    expect(screen.getByTestId('error-title')).toHaveTextContent('Error loading evidence')
  })
})
