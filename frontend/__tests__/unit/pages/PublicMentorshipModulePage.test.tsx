import { useQuery } from '@apollo/client/react'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useParams } from 'next/navigation'
import React from 'react'
import { render } from 'wrappers/testUtil'
import { handleAppError } from 'app/global-error'
import PublicMentorshipModulePage from 'app/mentorship/programs/[programKey]/modules/[moduleKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
}))

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title, message }: { title: string; message: string }) => (
    <div>
      <span>{title}</span>
      <span>{message}</span>
    </div>
  ),
}))

jest.mock('components/LoadingSpinner', () => () => <div>LoadingSpinner</div>)

jest.mock('components/CardDetailsPage/CardDetailsHeader', () => {
  return function MockHeader(props: { title: string }) {
    return <div data-testid="header">{props.title}</div>
  }
})

jest.mock('components/CardDetailsPage/CardDetailsSummary', () => {
  return function MockSummary(props: { summary: string }) {
    return <div data-testid="summary">{props.summary}</div>
  }
})

jest.mock('components/CardDetailsPage/CardDetailsPageWrapper', () => {
  return function MockWrapper({ children }: { children: React.ReactNode }) {
    return <div data-testid="wrapper">{children}</div>
  }
})

jest.mock('components/CardDetailsPage/CardDetailsMetadata', () => {
  return function MockMetadata() {
    return <div data-testid="metadata" />
  }
})

jest.mock('components/CardDetailsPage/CardDetailsTags', () => {
  return function MockTags() {
    return <div data-testid="tags" />
  }
})

jest.mock('components/CardDetailsPage/CardDetailsContributors', () => {
  return function MockContributors() {
    return <div data-testid="contributors" />
  }
})

jest.mock('components/CardDetailsPage/CardDetailsIssuesMilestones', () => {
  return function MockIssuesMilestones(props: {
    onLoadMorePullRequests?: () => void
    onResetPullRequests?: () => void
  }) {
    return (
      <div data-testid="issues-milestones">
        {props.onLoadMorePullRequests && (
          <button type="button" data-testid="pr-show-more" onClick={props.onLoadMorePullRequests}>
            Show more
          </button>
        )}
        {props.onResetPullRequests && (
          <button type="button" data-testid="pr-show-less" onClick={props.onResetPullRequests}>
            Show less
          </button>
        )}
        {props.isFetchingMore && <span data-testid="is-fetching">fetching</span>}
      </div>
    )
  }
})

const createPullRequest = (index: number) => ({
  id: `pr-${index}`,
  title: `PR ${index}`,
  url: `https://github.com/o/r/pull/${index}`,
  state: 'OPEN',
  createdAt: '2025-01-01T00:00:00Z',
  mergedAt: null,
  organizationName: 'org',
  repositoryName: 'repo',
  author: { id: 'a1', login: 'dev', name: 'Dev', avatarUrl: 'https://example.com/a.png' },
})

const buildModuleData = (prCount: number) => ({
  id: 'module-1',
  key: 'intro-web',
  name: 'Intro to Web',
  description: 'A public module.',
  experienceLevel: 'beginner',
  startedAt: '2025-01-01T00:00:00Z',
  endedAt: '2025-06-01T00:00:00Z',
  mentors: [{ id: 'm1', login: 'mentor1', name: 'Mentor', avatarUrl: '' }],
  mentees: [],
  tags: ['t1'],
  domains: ['d1'],
  labels: [],
  projectId: null,
  projectName: null,
  recentPullRequests: Array.from({ length: prCount }, (_, i) => createPullRequest(i)),
})

describe('PublicMentorshipModulePage', () => {
  const mockUseParams = useParams as jest.Mock
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockFetchMore = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseParams.mockReturnValue({
      programKey: 'gsoc-2025',
      moduleKey: 'intro-web',
    })
  })

  it('shows loading spinner when loading and there is no cached data', () => {
    mockUseQuery.mockReturnValue({
      loading: true,
      data: undefined,
      error: undefined,
      fetchMore: mockFetchMore,
    })

    const { container } = render(<PublicMentorshipModulePage />)
    expect(container.textContent).toContain('LoadingSpinner')
  })

  it('shows error display and reports the error when the query fails', async () => {
    const err = new Error('GraphQL failure')
    mockUseQuery.mockReturnValue({
      loading: false,
      data: undefined,
      error: err,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    await waitFor(() => {
      expect(handleAppError).toHaveBeenCalledWith(err)
    })
    expect(screen.getByText('Error loading module')).toBeInTheDocument()
  })

  it('shows not found when module data is missing', () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: { getModule: null, getProgram: { admins: [] } },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    expect(screen.getByText('Module Not Found')).toBeInTheDocument()
  })

  it('renders module details when data loads successfully', () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: buildModuleData(2),
        getProgram: { admins: [{ id: '1', login: 'admin1', name: 'A', avatarUrl: '' }] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    expect(screen.getByTestId('wrapper')).toHaveTextContent('Intro to Web')
    expect(screen.getByTestId('wrapper')).toHaveTextContent('A public module.')
  })

  it('omits load-more handler when there are no extra pull requests to page', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: buildModuleData(3),
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    await waitFor(() => {
      expect(screen.queryByTestId('pr-show-more')).not.toBeInTheDocument()
    })
  })

  it('invokes fetchMore when more PRs can be loaded from the server', async () => {
    const moduleData = buildModuleData(5)
    mockFetchMore.mockResolvedValue({})

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: moduleData,
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalledWith(
        expect.objectContaining({
          variables: expect.objectContaining({
            programKey: 'gsoc-2025',
            moduleKey: 'intro-web',
            offset: 5,
            limit: 4,
          }),
        })
      )
    })
  })

  it('does not invoke fetchMore again while a fetch is already in progress', async () => {
    let resolveFetch: (value: unknown) => void = () => {}
    const fetchPromise = new Promise((resolve) => {
      resolveFetch = resolve
    })
    mockFetchMore.mockReturnValue(fetchPromise)

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: buildModuleData(6),
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    fireEvent.click(screen.getByTestId('pr-show-more'))
    await waitFor(() => {
      expect(screen.getByTestId('is-fetching')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByTestId('pr-show-more'))

    expect(mockFetchMore).toHaveBeenCalledTimes(1)
    resolveFetch({})
    await waitFor(() => {
      expect(screen.queryByTestId('is-fetching')).not.toBeInTheDocument()
    })
  })

  it('reports fetchMore failures via handleAppError', async () => {
    const networkError = new Error('network down')
    mockFetchMore.mockRejectedValue(networkError)

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: buildModuleData(5),
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(handleAppError).toHaveBeenCalledWith(networkError)
    })
  })

  it('merges fetchMore results when the server returns additional pull requests', async () => {
    const initial = buildModuleData(5)
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        const merged = updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          {
            fetchMoreResult: {
              getModule: {
                recentPullRequests: [createPullRequest(10), createPullRequest(11)],
              },
            },
          }
        )
        return Promise.resolve(merged)
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: initial,
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  it('returns previous cache when fetchMore returns no result payload', async () => {
    const initial = buildModuleData(5)
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          { fetchMoreResult: undefined }
        )
        return Promise.resolve()
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: initial,
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  it('returns previous cache when fetchMore returns an empty pull request list', async () => {
    const initial = buildModuleData(5)
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          { fetchMoreResult: { getModule: { recentPullRequests: [] } } }
        )
        return Promise.resolve()
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: initial,
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  it('exposes reset handler after expanding beyond the first page of pull requests', async () => {
    mockFetchMore.mockResolvedValue({})

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: buildModuleData(6),
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    fireEvent.click(screen.getByTestId('pr-show-more'))
    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })

    expect(screen.getByTestId('pr-show-less')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('pr-show-less'))
  })

  it('treats a missing getModule payload in fetchMoreResult as an empty pull request batch', async () => {
    const initial = buildModuleData(5)
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          { fetchMoreResult: {} as { getModule?: { recentPullRequests: unknown[] } } }
        )
        return Promise.resolve()
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: initial,
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  it('marks pagination complete when fewer than a full page of pull requests is returned', async () => {
    const initial = buildModuleData(5)
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          {
            fetchMoreResult: {
              getModule: { recentPullRequests: [createPullRequest(99)] },
            },
          }
        )
        return Promise.resolve()
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: initial,
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  it('renders with null mentors, mentees, tags, and domains (covers ?? undefined fallbacks)', () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: {
          ...buildModuleData(2),
          mentors: null,
          mentees: null,
          tags: null,
          domains: null,
        },
        getProgram: { admins: null },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    expect(screen.getByTestId('wrapper')).toBeInTheDocument()
  })

  it('shows load-more button when local PRs exceed visibleCount even when hasMorePRs is false', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: buildModuleData(4),
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    await waitFor(() => {
      expect(screen.getByTestId('pr-show-more')).toBeInTheDocument()
    })
  })

  it('only increments visibleCount (no fetchMore) when hasMorePRs is false but local PRs exceed visibleCount', async () => {
    const initial = { ...buildModuleData(5) }
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          { fetchMoreResult: { getModule: { recentPullRequests: [] } } }
        )
        return Promise.resolve()
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: { getModule: initial, getProgram: { admins: [] } },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => expect(mockFetchMore).toHaveBeenCalledTimes(1))
    await waitFor(() => {
      expect(screen.queryByTestId('pr-show-more')).not.toBeInTheDocument()
    })
  })

  it('merges fetchMore results when prevResult has no existing pull requests', async () => {
    const initial = buildModuleData(5)
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        const merged = updateQuery(
          {
            getModule: { ...initial, recentPullRequests: null },
            getProgram: { admins: [] },
          },
          {
            fetchMoreResult: {
              getModule: {
                recentPullRequests: [createPullRequest(10), createPullRequest(11)],
              },
            },
          }
        )
        return Promise.resolve(merged)
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: { getModule: initial, getProgram: { admins: [] } },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  it('shows no load-more button when hasMorePRs is false and local PRs do not exceed visibleCount', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: buildModuleData(2),
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    await waitFor(() => {
      expect(screen.queryByTestId('pr-show-more')).not.toBeInTheDocument()
    })
  })

  it('uses || [] fallback on lines 120 and 163 when recentPullRequests is null', async () => {
    mockFetchMore.mockResolvedValue({})
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: { ...buildModuleData(0), recentPullRequests: null },
        getProgram: { admins: [] },
      },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    await waitFor(() => {
      expect(screen.getByTestId('pr-show-more')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  it('increments visibleCount without calling fetchMore when hasMorePRs is false and handler is clicked', async () => {
    const initial = buildModuleData(8)

    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          { fetchMoreResult: { getModule: { recentPullRequests: [] } } }
        )
        return Promise.resolve()
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: { getModule: initial, getProgram: { admins: [] } },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)

    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).not.toHaveBeenCalled()
    })
  })

  it('sets hasMorePRs to false when newPRs returned is less than limit (line 141)', async () => {
    const initial = buildModuleData(5)
    mockFetchMore.mockImplementation(
      ({ updateQuery }: { updateQuery: (p: unknown, o: unknown) => unknown }) => {
        updateQuery(
          { getModule: initial, getProgram: { admins: [] } },
          {
            fetchMoreResult: {
              getModule: {
                recentPullRequests: [createPullRequest(20), createPullRequest(21)],
              },
            },
          }
        )
        return Promise.resolve()
      }
    )

    mockUseQuery.mockReturnValue({
      loading: false,
      data: { getModule: initial, getProgram: { admins: [] } },
      error: undefined,
      fetchMore: mockFetchMore,
    })

    render(<PublicMentorshipModulePage />)
    fireEvent.click(screen.getByTestId('pr-show-more'))

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(screen.queryByTestId('pr-show-more')).not.toBeInTheDocument()
    })
  })
})
