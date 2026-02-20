import { useQuery, useApolloClient } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import BoardCandidatesPage from 'app/board/[year]/candidates/page'
import {
  GetBoardCandidatesDocument,
  GetMemberSnapshotDocument,
} from 'types/__generated__/boardQueries.generated'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ year: '2025' })),
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

jest.mock('next/image', () => ({
  __esModule: true,
  // Mock uses img for simplicity in tests; next/image is not used in test DOM.
  default: ({ src, alt }: { src: string; alt: string }) => (
    // eslint-disable-next-line @next/next/no-img-element -- test mock
    <img src={src} alt={alt} />
  ),
}))

jest.mock('components/ContributionHeatmap', () => ({
  __esModule: true,
  default: () => <div data-testid="contribution-heatmap" />,
}))

const mockBoardData = {
  boardOfDirectors: {
    id: 'board-1',
    year: 2025,
    owaspUrl: 'https://owasp.org',
    candidates: [
      {
        id: 'candidate-1',
        memberName: 'Alice Smith',
        memberEmail: 'alice@example.com',
        description: 'Platform and security experience.',
        member: {
          id: 'user-1',
          login: 'alice',
          name: 'Alice Smith',
          avatarUrl: 'https://example.com/avatar.png',
          bio: 'Security lead.',
          createdAt: 1609459200,
          firstOwaspContributionAt: 1609459200,
          isOwaspBoardMember: false,
          isFormerOwaspStaff: false,
          isGsocMentor: false,
          linkedinPageId: '',
        },
      },
    ],
  },
}

const mockUseQuery = useQuery as unknown as jest.Mock
const mockUseApolloClient = useApolloClient as unknown as jest.Mock

describe('BoardCandidatesPage', () => {
  beforeEach(() => {
    mockUseApolloClient.mockReturnValue({
      query: jest.fn().mockResolvedValue({ data: {} }),
    })
    mockUseQuery.mockImplementation(
      (document: unknown, _options?: { variables?: Record<string, unknown> }) => {
        if (document === GetBoardCandidatesDocument) {
          return {
            data: mockBoardData,
            loading: false,
            error: null,
          }
        }
        if (document === GetMemberSnapshotDocument) {
          return {
            data: { memberSnapshot: null },
            loading: false,
            error: null,
          }
        }
        return { data: null, loading: false, error: null }
      }
    )
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state when query is loading', () => {
    mockUseQuery.mockImplementation((document: unknown) => {
      if (document === GetBoardCandidatesDocument) {
        return { data: null, loading: true, error: null }
      }
      return { data: { memberSnapshot: null }, loading: false, error: null }
    })

    render(<BoardCandidatesPage />)

    const loadingIndicators = screen.getAllByAltText('Loading indicator')
    expect(loadingIndicators.length).toBeGreaterThan(0)
  })

  test('renders 404 when board data is missing', async () => {
    mockUseQuery.mockImplementation((document: unknown) => {
      if (document === GetBoardCandidatesDocument) {
        return { data: null, loading: false, error: null }
      }
      return { data: { memberSnapshot: null }, loading: false, error: null }
    })

    render(<BoardCandidatesPage />)

    await waitFor(() => {
      expect(screen.getByTestId('error-display')).toBeInTheDocument()
    })
    expect(screen.getByTestId('error-title')).toHaveTextContent('Board not found')
  })

  test('renders page title and year when board exists', async () => {
    render(<BoardCandidatesPage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
        '2025 Board of Directors Candidates'
      )
    })
  })

  test('renders empty state when no candidates', async () => {
    mockUseQuery.mockImplementation((document: unknown) => {
      if (document === GetBoardCandidatesDocument) {
        return {
          data: {
            boardOfDirectors: {
              ...mockBoardData.boardOfDirectors,
              candidates: [],
            },
          },
          loading: false,
          error: null,
        }
      }
      return { data: { memberSnapshot: null }, loading: false, error: null }
    })

    render(<BoardCandidatesPage />)

    await waitFor(() => {
      expect(screen.getByText(/No candidates found for 2025/)).toBeInTheDocument()
    })
  })

  test('renders candidate cards when candidates exist', async () => {
    render(<BoardCandidatesPage />)

    await waitFor(() => {
      expect(screen.getByText('Alice Smith')).toBeInTheDocument()
    })
    expect(screen.getByText(/Platform and security experience/)).toBeInTheDocument()
  })

  test('calls handleAppError when board query errors', async () => {
    const { handleAppError } = await import('app/global-error')
    const graphQLError = new Error('GraphQL error')
    mockUseQuery.mockImplementation((document: unknown) => {
      if (document === GetBoardCandidatesDocument) {
        return { data: null, loading: false, error: graphQLError }
      }
      return { data: { memberSnapshot: null }, loading: false, error: null }
    })

    render(<BoardCandidatesPage />)

    await waitFor(() => {
      expect(handleAppError).toHaveBeenCalledWith(graphQLError)
    })
  })
})
