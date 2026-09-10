import { useLazyQuery } from '@apollo/client/react'
import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import {
  GetSnapshotEntityIssuesDocument,
  GetSnapshotEntityPullRequestsDocument,
} from 'types/__generated__/snapshotQueries.generated'
import SnapshotEntitySection from 'components/SnapshotEntitySection'

jest.mock('@apollo/client/react', () => ({
  useLazyQuery: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
}))

const mockPRs = Array.from({ length: 7 }, (_, i) => ({
  id: `pr-${i}`,
  author: {
    avatarUrl: `https://avatars.githubusercontent.com/u/${i}?v=4`,
    id: `${i}`,
    login: `user${i}`,
    name: `User ${i}`,
  },
  createdAt: `2024-12-${10 + i}T09:00:00.000Z`,
  mergedAt: null,
  organizationName: 'owasp',
  repositoryName: 'nest',
  state: 'open',
  title: `PR ${i}`,
  url: `https://github.com/owasp/nest/pull/${100 + i}`,
}))

const mockIssues = Array.from({ length: 7 }, (_, i) => ({
  id: `issue-${i}`,
  author: {
    avatarUrl: `https://avatars.githubusercontent.com/u/${i}?v=4`,
    id: `${i}`,
    login: `user${i}`,
    name: `User ${i}`,
  },
  createdAt: `2024-12-${10 + i}T08:00:00.000Z`,
  organizationName: 'owasp',
  repositoryName: 'nest',
  state: 'open',
  title: `Issue ${i}`,
  url: `https://github.com/owasp/nest/issues/${100 + i}`,
}))

const mockReleases = [
  {
    id: 'release-1',
    name: 'v1.0.0',
    publishedAt: '2024-12-15T00:00:00.000Z',
    tagName: 'v1.0.0',
  },
]

const defaultProps = {
  snapshotKey: '2024-12',
  entityName: 'OWASP Nest',
  entityType: 'Project',
  repositoryNames: ['nest'],
  releases: mockReleases,
  initialPRs: mockPRs,
  initialIssues: mockIssues,
}

describe('SnapshotEntitySection', () => {
  beforeEach(() => {
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([
      jest.fn().mockResolvedValue({ data: {} }),
    ])
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders entity name and type badge', () => {
    render(<SnapshotEntitySection {...defaultProps} />)
    expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    expect(screen.getByText('Project')).toBeInTheDocument()
  })

  it('renders Issues section when issues are provided', () => {
    render(<SnapshotEntitySection {...defaultProps} />)
    expect(screen.getByText('Issues')).toBeInTheDocument()
  })

  it('renders Pull Requests section when PRs are provided', () => {
    render(<SnapshotEntitySection {...defaultProps} />)
    expect(screen.getByText('Pull Requests')).toBeInTheDocument()
  })

  it('renders Releases section when releases are provided', () => {
    render(<SnapshotEntitySection {...defaultProps} />)
    expect(screen.getByText('Releases')).toBeInTheDocument()
  })

  it('returns null when no PRs, issues, or releases', () => {
    render(
      <SnapshotEntitySection {...defaultProps} initialPRs={[]} initialIssues={[]} releases={[]} />
    )
    expect(screen.queryByText('OWASP Nest')).not.toBeInTheDocument()
    expect(screen.queryByText('Pull Requests')).not.toBeInTheDocument()
    expect(screen.queryByText('Issues')).not.toBeInTheDocument()
    expect(screen.queryByText('Releases')).not.toBeInTheDocument()
  })

  it('shows Show more button for PRs when there are more than 6', () => {
    render(<SnapshotEntitySection {...defaultProps} />)
    const prSection = screen.getByText('Pull Requests').closest('div')
    expect(prSection).toBeTruthy()
    expect(within(prSection!).getByText('Show more')).toBeInTheDocument()
  })

  it('shows Show more button for issues when there are more than 6', () => {
    render(<SnapshotEntitySection {...defaultProps} />)
    const issueSection = screen.getByText('Issues').closest('div')
    expect(issueSection).toBeTruthy()
    expect(within(issueSection!).getByText('Show more')).toBeInTheDocument()
  })

  it('hides sections when data arrays are empty', () => {
    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={[]}
        releases={mockReleases}
      />
    )
    expect(screen.queryByText('Pull Requests')).not.toBeInTheDocument()
    expect(screen.queryByText('Issues')).not.toBeInTheDocument()
    expect(screen.getByText('Releases')).toBeInTheDocument()
  })

  it('renders entity type as a badge', () => {
    render(<SnapshotEntitySection {...defaultProps} />)
    const badge = screen.getByText('Project')
    expect(badge.className).toContain('rounded-full')
  })

  it('paginates PRs locally when more data is already loaded than visible', async () => {
    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={mockPRs}
        initialIssues={[]}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Pull Requests')).toBeInTheDocument()
    })

    expect(screen.queryByText('PR 6')).not.toBeInTheDocument()

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('PR 6')).toBeInTheDocument()
    })
  })

  it('paginates issues locally when more data is already loaded than visible', async () => {
    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={mockIssues}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Issues')).toBeInTheDocument()
    })

    expect(screen.queryByText('Issue 6')).not.toBeInTheDocument()

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)
    await waitFor(() => {
      expect(screen.getByText('Issue 6')).toBeInTheDocument()
    })
  })
  it('fetches and appends new PRs from server when Show more is clicked', async () => {
    const newPR = {
      id: 'pr-new',
      author: null,
      createdAt: '2024-12-20T09:00:00.000Z',
      mergedAt: null,
      organizationName: 'owasp',
      repositoryName: 'nest',
      state: 'open',
      title: 'New Fetched PR',
      url: 'https://github.com/owasp/nest/pull/200',
    }
    const mockFetchPRs = jest.fn().mockResolvedValue({
      data: {
        snapshot: {
          pullRequests: [newPR],
        },
      },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockImplementation((document) =>
      document === GetSnapshotEntityPullRequestsDocument
        ? [mockFetchPRs]
        : [jest.fn().mockResolvedValue({ data: {} })]
    )

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={mockPRs.slice(0, 6)}
        initialIssues={[]}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Pull Requests')).toBeInTheDocument()
    })

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(mockFetchPRs).toHaveBeenCalled()
    })
    expect(mockFetchPRs).toHaveBeenCalledWith({
      variables: {
        key: '2024-12',
        limit: 6,
        offset: 6,
        repositoryNames: ['nest'],
      },
    })
    await waitFor(() => {
      expect(screen.getByText('New Fetched PR')).toBeInTheDocument()
    })
  })

  it('fetches and appends new issues from server when Show more is clicked', async () => {
    const newIssue = {
      id: 'issue-new',
      author: null,
      createdAt: '2024-12-20T08:00:00.000Z',
      organizationName: 'owasp',
      repositoryName: 'nest',
      state: 'open',
      title: 'New Fetched Issue',
      url: 'https://github.com/owasp/nest/issues/200',
    }
    const mockFetchIssues = jest.fn().mockResolvedValue({
      data: {
        snapshot: {
          issues: [newIssue],
        },
      },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockImplementation((document) =>
      document === GetSnapshotEntityIssuesDocument
        ? [mockFetchIssues]
        : [jest.fn().mockResolvedValue({ data: {} })]
    )

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={mockIssues.slice(0, 6)}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Issues')).toBeInTheDocument()
    })

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('New Fetched Issue')).toBeInTheDocument()
    })
  })

  it('handles PR fetch error gracefully', async () => {
    const mockFetchPRs = jest.fn().mockRejectedValue(new Error('Network error'))
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchPRs])

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={mockPRs.slice(0, 6)}
        initialIssues={[]}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Pull Requests')).toBeInTheDocument()
    })

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(mockFetchPRs).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('Show more')).toBeInTheDocument()
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
    })
  })

  it('handles issue fetch error gracefully', async () => {
    const mockFetchIssues = jest.fn().mockRejectedValue(new Error('Network error'))
    ;(useLazyQuery as unknown as jest.Mock).mockImplementation((document) =>
      document === GetSnapshotEntityIssuesDocument
        ? [mockFetchIssues]
        : [jest.fn().mockResolvedValue({ data: {} })]
    )

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={mockIssues.slice(0, 6)}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Issues')).toBeInTheDocument()
    })

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.getByText('Show more')).toBeInTheDocument()
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
    })
  })

  it('resets PR visible count when Show less is clicked', async () => {
    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={mockPRs}
        initialIssues={[]}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Pull Requests')).toBeInTheDocument()
    })

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('PR 6')).toBeInTheDocument()
    })

    const showLessButton = screen.getByText('Show less')
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('PR 6')).not.toBeInTheDocument()
    })
  })

  it('resets issue visible count when Show less is clicked', async () => {
    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={mockIssues}
        releases={[]}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Issues')).toBeInTheDocument()
    })

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Issue 6')).toBeInTheDocument()
    })

    const showLessButton = screen.getByText('Show less')
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Issue 6')).not.toBeInTheDocument()
    })
  })

  it('does not sync when initial data is empty', () => {
    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={[]}
        releases={mockReleases}
      />
    )
    expect(screen.getByText('Releases')).toBeInTheDocument()
    expect(screen.queryByText('Pull Requests')).not.toBeInTheDocument()
    expect(screen.queryByText('Issues')).not.toBeInTheDocument()
  })

  it('does not fetch more PRs when hasMorePRs is false', async () => {
    const fewPRs = mockPRs.slice(0, 3)
    const mockFetchPRs = jest.fn().mockResolvedValue({ data: {} })
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchPRs])

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={fewPRs}
        initialIssues={[]}
        releases={[]}
      />
    )

    expect(screen.getByText('Pull Requests')).toBeInTheDocument()
    expect(screen.queryByText('Show more')).not.toBeInTheDocument()
  })

  it('does not fetch more issues when hasMoreIssues is false', async () => {
    const fewIssues = mockIssues.slice(0, 3)
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([
      jest.fn().mockResolvedValue({ data: {} }),
    ])

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={fewIssues}
        releases={[]}
      />
    )

    expect(screen.getByText('Issues')).toBeInTheDocument()
    expect(screen.queryByText('Show more')).not.toBeInTheDocument()
  })

  it('sets hasMorePRs to false when server returns fewer than PR_LIMIT', async () => {
    const singlePR = {
      id: 'pr-extra',
      author: null,
      createdAt: '2024-12-20T09:00:00.000Z',
      mergedAt: null,
      organizationName: 'owasp',
      repositoryName: 'nest',
      state: 'open',
      title: 'Extra PR',
      url: 'https://github.com/owasp/nest/pull/300',
    }
    const mockFetchPRs = jest.fn().mockResolvedValue({
      data: { snapshot: { pullRequests: [singlePR] } },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchPRs])

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={mockPRs.slice(0, 6)}
        initialIssues={[]}
        releases={[]}
      />
    )

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Extra PR')).toBeInTheDocument()
    })
    expect(screen.getByText('Show less')).toBeInTheDocument()
  })

  it('sets hasMoreIssues to false when server returns empty array', async () => {
    const mockFetchIssues = jest.fn().mockResolvedValue({
      data: { snapshot: { issues: [] } },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockImplementation((document) =>
      document === GetSnapshotEntityIssuesDocument
        ? [mockFetchIssues]
        : [jest.fn().mockResolvedValue({ data: {} })]
    )

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={mockIssues.slice(0, 6)}
        releases={[]}
      />
    )

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(screen.queryByText('Show more')).not.toBeInTheDocument()
    })
  })

  it('handles server returning null pullRequests gracefully', async () => {
    const mockFetchPRs = jest.fn().mockResolvedValue({
      data: { snapshot: { pullRequests: null } },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchPRs])

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={mockPRs.slice(0, 6)}
        initialIssues={[]}
        releases={[]}
      />
    )

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(mockFetchPRs).toHaveBeenCalled()
    })
  })

  it('handles server returning null issues gracefully', async () => {
    const mockFetchIssues = jest.fn().mockResolvedValue({
      data: { snapshot: { issues: null } },
    })
    ;(useLazyQuery as unknown as jest.Mock).mockImplementation((document) =>
      document === GetSnapshotEntityIssuesDocument
        ? [mockFetchIssues]
        : [jest.fn().mockResolvedValue({ data: {} })]
    )

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={mockIssues.slice(0, 6)}
        releases={[]}
      />
    )

    const showMoreButton = screen.getByText('Show more')
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalled()
    })
  })

  it('toggles release visibility when onToggle is clicked', async () => {
    const manyReleases = Array.from({ length: 10 }, (_, i) => ({
      id: `release-${i}`,
      name: `v${i}.0.0`,
      publishedAt: `2024-12-${10 + i}T00:00:00.000Z`,
      tagName: `v${i}.0.0`,
      organizationName: 'owasp',
      repositoryName: 'nest',
    }))

    render(
      <SnapshotEntitySection
        {...defaultProps}
        initialPRs={[]}
        initialIssues={[]}
        releases={manyReleases}
      />
    )

    expect(screen.getByText('Releases')).toBeInTheDocument()
    const toggleButton = screen.getByText('Show more')
    fireEvent.click(toggleButton)
    await waitFor(() => {
      expect(screen.getByText('v9.0.0')).toBeInTheDocument()
    })
  })
})
