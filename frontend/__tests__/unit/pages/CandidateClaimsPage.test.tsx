import { useQuery, useMutation } from '@apollo/client/react'
import { mockClaims, mockCandidateData } from '@mockData/mockClaimData'
import { screen, waitFor } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { render } from 'wrappers/testUtil'
import CandidateClaimsPage from 'app/board/[year]/candidates/[login]/claims/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ login: 'testuser', year: '2025' })),
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
}))

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseMutation = useMutation as unknown as jest.Mock
const mockReorderFn = jest.fn()
const mockUseDjangoSession = useDjangoSession as jest.Mock
const stableData = { boardCandidateClaims: mockClaims, ...mockCandidateData }

describe('CandidateClaimsPage', () => {
  beforeEach(() => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'testuser' } },
      status: 'authenticated',
    })
    mockUseMutation.mockReturnValue([mockReorderFn, { loading: false }])
    mockUseQuery.mockReturnValue({ data: stableData, loading: false, error: null })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when query is loading', () => {
    mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

    render(<CandidateClaimsPage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders access denied when user is not a candidate', () => {
    mockUseQuery.mockReturnValue({
      data: { boardCandidateClaims: [], boardOfDirectors: { candidate: null } },
      loading: false,
      error: null,
    })

    render(<CandidateClaimsPage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders access denied when viewing another user profile', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: { user: { login: 'otheruser' } },
      status: 'authenticated',
    })

    render(<CandidateClaimsPage />)

    expect(screen.getByText('Access Denied')).toBeInTheDocument()
  })

  test('renders page title and create button', async () => {
    render(<CandidateClaimsPage />)

    await waitFor(() => {
      expect(screen.getByText('Your Claims')).toBeInTheDocument()
    })
    expect(screen.getByText('Create Claim')).toBeInTheDocument()
  })

  test('renders claims grouped by status sections', async () => {
    render(<CandidateClaimsPage />)

    await waitFor(() => {
      expect(screen.getByText('Draft Claims')).toBeInTheDocument()
    })
    expect(screen.getByText('Submitted Claims')).toBeInTheDocument()
    expect(screen.getByText('Approved Claims')).toBeInTheDocument()
    expect(screen.getByText('Rejected Claims')).toBeInTheDocument()
    expect(screen.getByText('Withdrawn Claims')).toBeInTheDocument()
  })

  test('renders claim names and descriptions', async () => {
    render(<CandidateClaimsPage />)

    await waitFor(() => {
      expect(screen.getByText('Leadership Experience')).toBeInTheDocument()
    })
    expect(screen.getByText('Chapter Leadership')).toBeInTheDocument()
    expect(screen.getByText('Approved Claim')).toBeInTheDocument()
  })

  test('renders evidence badge for claims with evidence', async () => {
    render(<CandidateClaimsPage />)

    await waitFor(() => {
      expect(screen.getAllByText('Evidence').length).toBeGreaterThanOrEqual(1)
    })
  })

  test('renders empty state when no claims exist', async () => {
    mockUseQuery.mockReturnValue({
      data: { boardCandidateClaims: [], ...mockCandidateData },
      loading: false,
      error: null,
    })

    render(<CandidateClaimsPage />)

    await waitFor(() => {
      expect(screen.getByText('No draft claims.')).toBeInTheDocument()
    })
  })
})
