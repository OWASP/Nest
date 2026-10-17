import { useQuery, useApolloClient } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import BoardCandidatesPage from 'app/board/[year]/candidates/page'
import {
  GetBoardCandidatesDocument,
  GetChapterByKeyDocument,
  GetMemberSnapshotDocument,
  GetProjectByKeyDocument,
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

  describe('contribution labels for led chapters and projects', () => {
    const buildSnapshot = (
      chapterContributions: Record<string, number>,
      projectContributions: Record<string, number>
    ) => ({
      id: 'snapshot-1',
      githubUser: { login: 'alice' },
      chapterContributions,
      projectContributions,
      channelCommunications: {},
      communicationHeatmapData: {},
      contributionHeatmapData: {},
      repositoryContributions: {},
      commitsCount: 0,
      issuesCount: 0,
      messagesCount: 0,
      pullRequestsCount: 0,
      totalContributions: 0,
      startAt: '2025-01-01T00:00:00Z',
      endAt: '2025-12-31T00:00:00Z',
    })

    const renderWithSnapshot = ({
      chapterContributions = {},
      projectContributions = {},
      chapterKey = 'london',
      projectKey = 'nest',
    }: {
      chapterContributions?: Record<string, number>
      projectContributions?: Record<string, number>
      chapterKey?: string
      projectKey?: string
    }) => {
      const boardResult = { data: mockBoardData, loading: false, error: null }
      const snapshotResult = {
        data: { memberSnapshot: buildSnapshot(chapterContributions, projectContributions) },
        loading: false,
        error: null,
      }
      mockUseQuery.mockImplementation((document: unknown) => {
        if (document === GetBoardCandidatesDocument) {
          return boardResult
        }
        if (document === GetMemberSnapshotDocument) {
          return snapshotResult
        }
        return { data: null, loading: false, error: null }
      })
      mockUseApolloClient.mockReturnValue({
        query: jest.fn().mockImplementation(({ query }: { query: unknown }) => {
          if (query === GetChapterByKeyDocument) {
            return Promise.resolve({
              data: {
                chapter: {
                  id: 'chapter-1',
                  key: chapterKey,
                  name: 'London Chapter',
                  url: 'https://owasp.org/www-chapter-london',
                },
              },
            })
          }
          if (query === GetProjectByKeyDocument) {
            return Promise.resolve({
              data: {
                project: {
                  id: 'project-1',
                  key: projectKey,
                  level: 'flagship',
                  name: 'Nest Project',
                  type: 'code',
                  url: 'https://owasp.org/www-project-nest',
                },
              },
            })
          }
          return Promise.resolve({ data: {} })
        }),
      })
      render(<BoardCandidatesPage />)
    }

    const chapterCases: Array<[string, Record<string, number>, string, string]> = [
      [
        'prefixed snapshot key, bare chapter key',
        { 'www-chapter-london': 7 },
        'london',
        '7 contributions',
      ],
      [
        'bare snapshot key, prefixed chapter key',
        { london: 4 },
        'www-chapter-london',
        '4 contributions',
      ],
      [
        'exact key with a zero count',
        { 'www-chapter-london': 0 },
        'www-chapter-london',
        'no contributions',
      ],
      ['no matching key', { 'www-chapter-paris': 3 }, 'london', 'no contributions'],
    ]

    test.each(chapterCases)(
      'chapter: %s',
      async (_name, chapterContributions, chapterKey, expected) => {
        renderWithSnapshot({ chapterContributions, chapterKey })

        const link = await screen.findByRole('link', { name: /London Chapter/ })
        expect(link).toHaveTextContent(expected)
      }
    )

    const projectCases: Array<[string, Record<string, number>, string, string]> = [
      [
        'prefixed snapshot key, bare project key',
        { 'www-project-nest': 5 },
        'nest',
        '5 contributions',
      ],
      [
        'bare snapshot key, prefixed project key',
        { nest: 2 },
        'www-project-nest',
        '2 contributions',
      ],
      [
        'exact key with a zero count',
        { 'www-project-nest': 0 },
        'www-project-nest',
        'no contributions',
      ],
      ['no matching key', { 'www-project-zap': 3 }, 'nest', 'no contributions'],
    ]

    test.each(projectCases)(
      'project: %s',
      async (_name, projectContributions, projectKey, expected) => {
        renderWithSnapshot({ projectContributions, projectKey })

        const link = await screen.findByRole('link', { name: /Nest Project/ })
        expect(link).toHaveTextContent(expected)
      }
    )
  })
})
