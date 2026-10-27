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

  const buildSnapshot = ({
    chapterContributions = {},
    projectContributions = {},
    repositoryContributions = {},
    channelCommunications = {},
  }: {
    chapterContributions?: Record<string, number>
    projectContributions?: Record<string, number>
    repositoryContributions?: Record<string, number>
    channelCommunications?: Record<string, number>
  }) => ({
    id: 'snapshot-1',
    githubUser: { login: 'alice' },
    chapterContributions,
    projectContributions,
    channelCommunications,
    communicationHeatmapData: {},
    contributionHeatmapData: {},
    repositoryContributions,
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
    repositoryContributions = {},
    channelCommunications = {},
    chapterKey = 'london',
    projectKey = 'nest',
  }: {
    chapterContributions?: Record<string, number>
    projectContributions?: Record<string, number>
    repositoryContributions?: Record<string, number>
    channelCommunications?: Record<string, number>
    chapterKey?: string
    projectKey?: string
  }) => {
    const boardResult = { data: mockBoardData, loading: false, error: null }
    const snapshotResult = {
      data: {
        memberSnapshot: buildSnapshot({
          chapterContributions,
          projectContributions,
          repositoryContributions,
          channelCommunications,
        }),
      },
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

  describe('contribution labels for led chapters and projects', () => {
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

  describe('top contribution lists', () => {
    const TOP_CONTRIBUTIONS_COUNT = 5

    const repositoryContributions = {
      'www-project-nest': 42,
      'www-project-juice-shop': 31,
      'www-project-nettacker': 25,
      'www-project-goatsecurity': 19,
      'www-project-chapter-london': 12,
      'www-project-mastodon': 8,
      'www-project-sbom': 5,
      'www-project-wstg': 2,
    }

    const channelCommunications = {
      general: 64,
      'project-nest': 41,
      appsec: 33,
      contributors: 27,
      'chapter-london': 14,
      'owasp-leaders': 9,
      gsoc: 6,
      random: 3,
    }

    test('renders at most five repositories under the top repositories heading', async () => {
      renderWithSnapshot({ repositoryContributions })

      expect(await screen.findByText('Top 5 Active Repositories')).toBeInTheDocument()
      expect(screen.getAllByRole('link', { name: /commits/ })).toHaveLength(TOP_CONTRIBUTIONS_COUNT)
    })

    test('renders the repositories with the highest commit counts first', async () => {
      renderWithSnapshot({ repositoryContributions })

      const links = await screen.findAllByRole('link', { name: /commits/ })

      expect(links.map((link) => link.textContent)).toEqual([
        'www-project-nest42 commits',
        'www-project-juice-shop31 commits',
        'www-project-nettacker25 commits',
        'www-project-goatsecurity19 commits',
        'www-project-chapter-london12 commits',
      ])
    })

    test('renders every repository when there are fewer than five', async () => {
      renderWithSnapshot({
        repositoryContributions: {
          'www-project-nest': 42,
          'www-project-juice-shop': 31,
          'www-project-nettacker': 25,
        },
      })

      expect(await screen.findAllByRole('link', { name: /commits/ })).toHaveLength(3)
    })

    test('renders at most five channels under the top channels heading', async () => {
      renderWithSnapshot({ channelCommunications })

      expect(await screen.findByText('Top 5 Active Channels')).toBeInTheDocument()
      expect(screen.getAllByRole('link', { name: /messages/ })).toHaveLength(
        TOP_CONTRIBUTIONS_COUNT
      )
    })

    test('renders the channels with the highest message counts first', async () => {
      renderWithSnapshot({ channelCommunications })

      const links = await screen.findAllByRole('link', { name: /messages/ })

      expect(links.map((link) => link.textContent)).toEqual([
        '#general64 messages',
        '#project-nest41 messages',
        '#appsec33 messages',
        '#contributors27 messages',
        '#chapter-london14 messages',
      ])
    })

    test('renders every channel when there are fewer than five', async () => {
      renderWithSnapshot({
        channelCommunications: { general: 64, appsec: 33, contributors: 27 },
      })

      expect(await screen.findAllByRole('link', { name: /messages/ })).toHaveLength(3)
    })
  })
})
