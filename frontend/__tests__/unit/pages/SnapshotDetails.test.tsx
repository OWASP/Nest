import { useQuery, useLazyQuery, useApolloClient } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { mockSnapshotDetailsData } from '@mockData/mockSnapshotData'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import SnapshotDetailsPage from 'app/community/snapshots/[id]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
  useLazyQuery: jest.fn(),
  useApolloClient: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ id: '2024-12' }),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

jest.mock('@/components/MarkdownWrapper', () => {
  return jest.fn(({ content, className }) => (
    <div className={`md-wrapper ${className}`} dangerouslySetInnerHTML={{ __html: content }} />
  ))
})

const findButtonInSection = (buttonText: string, sectionTitle: string) => {
  const heading = screen.getByText(sectionTitle)
  let container: Element | null = null
  if (heading.id) {
    container = document.querySelector(`[aria-labelledby="${heading.id}"]`)
  }
  if (!container) {
    container = heading.closest(
      '[role="region"], [role="group"], [role="article"], [role="toolbar"], section, article, div.shadow-md'
    )
  }
  if (!container) return undefined
  const buttons = container.querySelectorAll('button')
  for (const btn of Array.from(buttons)) {
    if (btn.textContent?.includes(buttonText)) return btn
  }
  return undefined
}

describe('SnapshotDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
      loading: false,
      error: null,
    })
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([
      jest.fn().mockResolvedValue({ data: {} }),
    ])
    ;(useApolloClient as jest.Mock).mockReturnValue({
      cache: {
        updateQuery: jest.fn(),
      },
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    render(<SnapshotDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders snapshot details when data is available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Snapshot')).toBeInTheDocument()
    })

    expect(screen.getByText('New Chapters')).toBeInTheDocument()
    expect(screen.getByText('New Projects')).toBeInTheDocument()
    expect(screen.getByText('New Releases')).toBeInTheDocument()
    expect(screen.getByText('New Events')).toBeInTheDocument()
    expect(screen.getByText('New Posts')).toBeInTheDocument()
    expect(screen.getByText('New Pull Requests')).toBeInTheDocument()
    expect(screen.getByText('New Issues')).toBeInTheDocument()
    expect(screen.getByText('New Contributors')).toBeInTheDocument()
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: mockError,
      loading: false,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => screen.getByText('Error loading snapshot'))
    expect(screen.getByText('Error loading snapshot')).toBeInTheDocument()
    expect(addToast).toHaveBeenCalledWith({
      description: 'An unexpected server error occurred.',
      title: 'Server Error',
      timeout: 5000,
      shouldShowTimeoutProgress: true,
      color: 'danger',
      variant: 'solid',
    })
  })

  test('displays "Snapshot not found" when data is null without error', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      loading: false,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => screen.getByText('Snapshot not found'))
    expect(screen.getByText('Snapshot not found')).toBeInTheDocument()
  })

  test('navigates to project page when project card is clicked', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })

    const projectButton = findButtonInSection('View Details', 'OWASP Nest')
    expect(projectButton).toBeDefined()
    fireEvent.click(projectButton!)

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/projects/nest')
    })
  })

  test('navigates to chapter page when chapter card is clicked', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Sivagangai')).toBeInTheDocument()
    })

    const chapterCardButton = screen.getAllByRole('button', { name: /View Details/i })[0]
    fireEvent.click(chapterCardButton)

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/chapters/sivagangai')
    })
  })

  test('renders new releases correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Snapshot')).toBeInTheDocument()
      expect(screen.getByText('Latest pre-release')).toBeInTheDocument()
    })

    expect(screen.getByText('test-project-1')).toBeInTheDocument()
    expect(screen.getByText('test-project-2')).toBeInTheDocument()
  })

  test('handles missing data gracefully', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          chapters: [],
          events: [],
          issues: [],
          posts: [],
          projects: [],
          pullRequests: [],
          releases: [],
          users: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.queryByText('New Chapters')).not.toBeInTheDocument()
      expect(screen.queryByText('New Events')).not.toBeInTheDocument()
      expect(screen.queryByText('New Issues')).not.toBeInTheDocument()
      expect(screen.queryByText('New Posts')).not.toBeInTheDocument()
      expect(screen.queryByText('New Projects')).not.toBeInTheDocument()
      expect(screen.queryByText('New Pull Requests')).not.toBeInTheDocument()
      expect(screen.queryByText('New Releases')).not.toBeInTheDocument()
      expect(screen.queryByText('New Contributors')).not.toBeInTheDocument()
    })
  })

  test('renders project card with null key (uses name fallback)', async () => {
    const projectWithNullKey = {
      ...mockSnapshotDetailsData.snapshot.projects[0],
      key: null,
      name: 'Test Project',
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          projects: [projectWithNullKey],
          chapters: [],
          releases: [],
        },
      },
      error: null,
      loading: false,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
  })

  test('renders project card without level', async () => {
    const projectWithoutLevel = {
      ...mockSnapshotDetailsData.snapshot.projects[0],
      level: undefined,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          projects: [projectWithoutLevel],
          chapters: [],
          releases: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })
  })

  test('renders project card without summary', async () => {
    const projectWithoutSummary = {
      ...mockSnapshotDetailsData.snapshot.projects[0],
      summary: undefined,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          projects: [projectWithoutSummary],
          chapters: [],
          releases: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })
  })

  test('renders chapter card without relatedUrls', async () => {
    const chapterWithoutUrls = {
      ...mockSnapshotDetailsData.snapshot.chapters[0],
      relatedUrls: undefined,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          chapters: [chapterWithoutUrls],
          projects: [],
          releases: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Sivagangai')).toBeInTheDocument()
    })
  })

  test('renders chapter card without summary', async () => {
    const chapterWithoutSummary = {
      ...mockSnapshotDetailsData.snapshot.chapters[0],
      summary: undefined,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          chapters: [chapterWithoutSummary],
          projects: [],
          releases: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Sivagangai')).toBeInTheDocument()
    })
  })

  test('filters out inactive chapters', async () => {
    const activeChapter = {
      ...mockSnapshotDetailsData.snapshot.chapters[0],
      name: 'Active Chapter',
      key: 'active-chapter',
      isActive: true,
    }
    const inactiveChapter = {
      ...mockSnapshotDetailsData.snapshot.chapters[0],
      name: 'Inactive Chapter',
      key: 'inactive-chapter',
      isActive: false,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          chapters: [activeChapter, inactiveChapter],
          projects: [],
          releases: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Active Chapter')).toBeInTheDocument()
    })
    expect(screen.queryByText('Inactive Chapter')).not.toBeInTheDocument()
  })

  test('filters out inactive projects', async () => {
    const activeProject = {
      ...mockSnapshotDetailsData.snapshot.projects[0],
      name: 'Active Project',
      key: 'active-project',
      isActive: true,
    }
    const inactiveProject = {
      ...mockSnapshotDetailsData.snapshot.projects[0],
      name: 'Inactive Project',
      key: 'inactive-project',
      isActive: false,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          projects: [activeProject, inactiveProject],
          chapters: [],
          releases: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Active Project')).toBeInTheDocument()
    })
    expect(screen.queryByText('Inactive Project')).not.toBeInTheDocument()
  })

  test('renders release without id (uses fallback key)', async () => {
    const releaseWithoutId = {
      ...mockSnapshotDetailsData.snapshot.releases[0],
      id: undefined,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          releases: [releaseWithoutId],
          chapters: [],
          projects: [],
        },
      },
      error: null,
      loading: false,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('v0.9.2')).toBeInTheDocument()
    })
  })

  test('renders release without id and repositoryName (uses unknown fallback)', async () => {
    const releaseWithoutIdAndRepo = {
      ...mockSnapshotDetailsData.snapshot.releases[0],
      id: undefined,
      repositoryName: undefined,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          releases: [releaseWithoutIdAndRepo],
          chapters: [],
          projects: [],
        },
      },
      error: null,
      loading: false,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('v0.9.2')).toBeInTheDocument()
      expect(screen.getByText('Unknown repository')).toBeInTheDocument()
    })
  })

  test('sorts events by priority: Global first, then AppSec Days, Partner, Other', async () => {
    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Events')).toBeInTheDocument()
    })

    const allH3s = screen.getAllByRole('heading', { level: 3 })
    const knownEventNames = new Set([
      'Global AppSec 2024',
      'Global Summit',
      'AppSec Days Pacific',
      'Partner Security Summit',
      'Local Meetup',
    ])
    const eventNames = allH3s
      .map((el) => el.textContent)
      .filter((name) => knownEventNames.has(name || ''))

    const globalIdx = eventNames.indexOf('Global AppSec 2024')
    const appsecIdx = eventNames.indexOf('AppSec Days Pacific')
    const partnerIdx = eventNames.indexOf('Partner Security Summit')
    const localIdx = eventNames.indexOf('Local Meetup')

    expect(globalIdx).toBeGreaterThanOrEqual(0)
    expect(appsecIdx).toBeGreaterThanOrEqual(0)
    expect(partnerIdx).toBeGreaterThanOrEqual(0)
    expect(localIdx).toBeGreaterThanOrEqual(0)

    expect(globalIdx).toBeLessThan(appsecIdx)
    expect(appsecIdx).toBeLessThan(partnerIdx)
    expect(partnerIdx).toBeLessThan(localIdx)
  })

  test('shows more events when Show more button is clicked', async () => {
    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Events')).toBeInTheDocument()
    })

    expect(screen.queryByText('Security Workshop')).not.toBeInTheDocument()

    const eventsShowMore = findButtonInSection('Show more', 'New Events')
    expect(eventsShowMore).toBeDefined()
    fireEvent.click(eventsShowMore!)

    await waitFor(() => {
      expect(screen.getByText('Security Workshop')).toBeInTheDocument()
    })
  })

  test('renders releases section with show more toggle', async () => {
    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Releases')).toBeInTheDocument()
      expect(screen.getByText('v0.9.2')).toBeInTheDocument()
      expect(screen.getByText('Latest pre-release')).toBeInTheDocument()
    })
  })

  test('shows more contributors when Show more button is clicked', async () => {
    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Contributors')).toBeInTheDocument()
    })

    expect(screen.queryByText('User Thirteen')).not.toBeInTheDocument()
    expect(screen.getAllByText('Arkadii Yakovets').length).toBeGreaterThanOrEqual(1)

    const contribShowMore = findButtonInSection('Show more', 'New Contributors')
    expect(contribShowMore).toBeDefined()
    fireEvent.click(contribShowMore!)

    await waitFor(() => {
      expect(screen.getByText('User Thirteen')).toBeInTheDocument()
    })
  })

  test('clicks Show more on pull requests to trigger pagination', async () => {
    const mockFetchMorePRs = jest.fn().mockResolvedValue({
      data: {
        snapshot: {
          pullRequests: [
            {
              id: 'pr-new',
              author: {
                avatarUrl: 'https://avatars.githubusercontent.com/u/99?v=4',
                id: '99',
                login: 'newuser',
                name: 'New PR User',
              },
              createdAt: '2024-12-20T09:00:00.000Z',
              mergedAt: null,
              organizationName: 'owasp',
              repositoryName: 'nest',
              state: 'open',
              title: 'Brand New PR',
              url: 'https://github.com/owasp/nest/pull/200',
            },
          ],
        },
      },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchMorePRs])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Pull Requests')).toBeInTheDocument()
    })

    expect(screen.queryByText('PR Seven')).not.toBeInTheDocument()

    const prShowMore = findButtonInSection('Show more', 'New Pull Requests')
    expect(prShowMore).toBeDefined()
    fireEvent.click(prShowMore!)

    await waitFor(() => {
      expect(screen.getByText('PR Seven')).toBeInTheDocument()
    })
  })

  test('clicks Show more on issues to trigger pagination', async () => {
    const mockFetchMoreIssues = jest.fn().mockResolvedValue({
      data: {
        snapshot: {
          issues: [
            {
              id: 'issue-new',
              author: {
                avatarUrl: 'https://avatars.githubusercontent.com/u/99?v=4',
                id: '99',
                login: 'newuser',
                name: 'New Issue User',
              },
              createdAt: '2024-12-20T08:00:00.000Z',
              organizationName: 'owasp',
              repositoryName: 'nest',
              state: 'open',
              title: 'Brand New Issue',
              url: 'https://github.com/owasp/nest/issues/200',
            },
          ],
        },
      },
    })
    ;(useLazyQuery as unknown as jest.Mock)
      .mockReturnValueOnce([jest.fn().mockResolvedValue({ data: {} })])
      .mockReturnValueOnce([mockFetchMoreIssues])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Issues')).toBeInTheDocument()
    })

    expect(screen.queryByText('Issue Seven')).not.toBeInTheDocument()

    const issueShowMore = findButtonInSection('Show more', 'New Issues')
    expect(issueShowMore).toBeDefined()
    fireEvent.click(issueShowMore!)

    await waitFor(() => {
      expect(screen.getByText('Issue Seven')).toBeInTheDocument()
    })
  })

  test('shows more posts when Show more button is clicked', async () => {
    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Posts')).toBeInTheDocument()
    })

    expect(screen.queryByText('Post Six')).not.toBeInTheDocument()

    const postsShowMore = findButtonInSection('Show more', 'New Posts')
    expect(postsShowMore).toBeDefined()
    fireEvent.click(postsShowMore!)

    await waitFor(() => {
      expect(screen.getByText('Post Six')).toBeInTheDocument()
    })
  })

  test('clicks Show less on pull requests to collapse', async () => {
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([
      jest.fn().mockResolvedValue({
        data: {
          snapshot: {
            pullRequests: [
              {
                id: 'pr-7',
                author: {
                  avatarUrl: 'https://avatars.githubusercontent.com/u/7?v=4',
                  id: '7',
                  login: 'user7',
                  name: 'User Seven',
                },
                createdAt: '2024-12-18T09:00:00.000Z',
                mergedAt: null,
                organizationName: 'owasp',
                repositoryName: 'nest',
                state: 'open',
                title: 'PR Seven',
                url: 'https://github.com/owasp/nest/pull/106',
              },
            ],
          },
        },
      }),
    ])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Pull Requests')).toBeInTheDocument()
    })

    const prShowMore = findButtonInSection('Show more', 'New Pull Requests')
    expect(prShowMore).toBeDefined()
    fireEvent.click(prShowMore!)

    await waitFor(() => {
      expect(screen.getByText('PR Seven')).toBeInTheDocument()
    })

    const prShowLess = findButtonInSection('Show less', 'New Pull Requests')
    expect(prShowLess).toBeDefined()
    fireEvent.click(prShowLess!)

    await waitFor(() => {
      expect(screen.queryByText('PR Seven')).not.toBeInTheDocument()
    })
  })

  test('clicks Show less on issues to collapse', async () => {
    ;(useLazyQuery as unknown as jest.Mock)
      .mockReturnValueOnce([jest.fn().mockResolvedValue({ data: {} })])
      .mockReturnValueOnce([
        jest.fn().mockResolvedValue({
          data: {
            snapshot: {
              issues: [
                {
                  id: 'issue-7',
                  author: {
                    avatarUrl: 'https://avatars.githubusercontent.com/u/7?v=4',
                    id: '7',
                    login: 'user7',
                    name: 'User Seven',
                  },
                  createdAt: '2024-12-17T08:00:00.000Z',
                  organizationName: 'owasp',
                  repositoryName: 'nest',
                  state: 'open',
                  title: 'Issue Seven',
                  url: 'https://github.com/owasp/nest/issues/56',
                },
              ],
            },
          },
        }),
      ])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Issues')).toBeInTheDocument()
    })

    const issueShowMore = findButtonInSection('Show more', 'New Issues')
    expect(issueShowMore).toBeDefined()
    fireEvent.click(issueShowMore!)

    await waitFor(() => {
      expect(screen.getByText('Issue Seven')).toBeInTheDocument()
    })

    const issueShowLess = findButtonInSection('Show less', 'New Issues')
    expect(issueShowLess).toBeDefined()
    fireEvent.click(issueShowLess!)

    await waitFor(() => {
      expect(screen.queryByText('Issue Seven')).not.toBeInTheDocument()
    })
  })

  test('PR fetchMore triggers cache update when new PRs are returned', async () => {
    const mockUpdateQuery = jest.fn()
    ;(useApolloClient as jest.Mock).mockReturnValue({
      cache: {
        updateQuery: mockUpdateQuery,
      },
    })

    const mockFetchMorePRs = jest.fn().mockResolvedValue({
      data: {
        snapshot: {
          pullRequests: [
            {
              id: 'pr-fetched',
              author: null,
              createdAt: '2024-12-20T09:00:00.000Z',
              mergedAt: null,
              organizationName: 'owasp',
              repositoryName: 'nest',
              state: 'open',
              title: 'Fetched PR',
              url: 'https://github.com/owasp/nest/pull/300',
            },
          ],
        },
      },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchMorePRs])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Pull Requests')).toBeInTheDocument()
    })

    const prShowMore = findButtonInSection('Show more', 'New Pull Requests')
    expect(prShowMore).toBeDefined()
    fireEvent.click(prShowMore!)

    await waitFor(() => {
      expect(mockFetchMorePRs).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(mockUpdateQuery).toHaveBeenCalled()
    })

    const updateFn = mockUpdateQuery.mock.calls[0][1]
    const prevData = {
      snapshot: {
        pullRequests: [{ id: 'existing-pr' }],
      },
    }
    const result = updateFn(prevData)
    expect(result.snapshot.pullRequests).toHaveLength(2)

    const nullResult = updateFn(null)
    expect(nullResult).toBeNull()
  })

  test('Issue fetchMore triggers cache update when new issues are returned', async () => {
    const mockUpdateQuery = jest.fn()
    ;(useApolloClient as jest.Mock).mockReturnValue({
      cache: {
        updateQuery: mockUpdateQuery,
      },
    })

    const mockFetchMoreIssues = jest.fn().mockResolvedValue({
      data: {
        snapshot: {
          issues: [
            {
              id: 'issue-fetched',
              author: null,
              createdAt: '2024-12-20T08:00:00.000Z',
              organizationName: 'owasp',
              repositoryName: 'nest',
              state: 'open',
              title: 'Fetched Issue',
              url: 'https://github.com/owasp/nest/issues/300',
            },
          ],
        },
      },
    })
    ;(useLazyQuery as unknown as jest.Mock)
      .mockReturnValueOnce([jest.fn().mockResolvedValue({ data: {} })])
      .mockReturnValueOnce([mockFetchMoreIssues])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Issues')).toBeInTheDocument()
    })

    const issueShowMore = findButtonInSection('Show more', 'New Issues')
    expect(issueShowMore).toBeDefined()
    fireEvent.click(issueShowMore!)

    await waitFor(() => {
      expect(mockFetchMoreIssues).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(mockUpdateQuery).toHaveBeenCalled()
    })

    const updateFn = mockUpdateQuery.mock.calls[0][1]
    const prevData = {
      snapshot: {
        issues: [{ id: 'existing-issue' }],
      },
    }
    const result = updateFn(prevData)
    expect(result.snapshot.issues).toHaveLength(2)

    const nullResult = updateFn(null)
    expect(nullResult).toBeNull()
  })

  test('shows more chapters when Show more button is clicked', async () => {
    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Chapters')).toBeInTheDocument()
    })

    expect(screen.queryByText('OWASP London')).not.toBeInTheDocument()
    expect(screen.getByText('OWASP Sivagangai')).toBeInTheDocument()

    const chaptersShowMore = findButtonInSection('Show more', 'New Chapters')
    expect(chaptersShowMore).toBeDefined()
    fireEvent.click(chaptersShowMore!)

    await waitFor(() => {
      expect(screen.getByText('OWASP London')).toBeInTheDocument()
    })
  })

  test('shows more projects when Show more button is clicked', async () => {
    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Projects')).toBeInTheDocument()
    })

    expect(screen.queryByText('OWASP SAMM')).not.toBeInTheDocument()
    expect(screen.getByText('OWASP Nest')).toBeInTheDocument()

    const projectsShowMore = findButtonInSection('Show more', 'New Projects')
    expect(projectsShowMore).toBeDefined()
    fireEvent.click(projectsShowMore!)

    await waitFor(() => {
      expect(screen.getByText('OWASP SAMM')).toBeInTheDocument()
    })
  })

  test('PR fetchMore error triggers handleAppError', async () => {
    const mockFetchMorePRs = jest.fn().mockRejectedValue(new Error('Network error'))
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchMorePRs])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Pull Requests')).toBeInTheDocument()
    })

    const prShowMore = findButtonInSection('Show more', 'New Pull Requests')
    expect(prShowMore).toBeDefined()
    fireEvent.click(prShowMore!)

    await waitFor(() => {
      expect(mockFetchMorePRs).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(addToast).toHaveBeenCalled()
    })
  })

  test('Issue fetchMore error triggers handleAppError', async () => {
    const mockFetchMoreIssues = jest.fn().mockRejectedValue(new Error('Network error'))
    ;(useLazyQuery as unknown as jest.Mock)
      .mockReturnValueOnce([jest.fn().mockResolvedValue({ data: {} })])
      .mockReturnValueOnce([mockFetchMoreIssues])

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Issues')).toBeInTheDocument()
    })

    const issueShowMore = findButtonInSection('Show more', 'New Issues')
    expect(issueShowMore).toBeDefined()
    fireEvent.click(issueShowMore!)

    await waitFor(() => {
      expect(mockFetchMoreIssues).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(addToast).toHaveBeenCalled()
    })
  })
})
