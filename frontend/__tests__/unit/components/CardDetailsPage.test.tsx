import { render, screen, cleanup } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { FaCode, FaTags } from 'react-icons/fa6'
import type { MenteeNode } from 'types/__generated__/graphql'
import type { DetailsCardProps } from 'types/card'
import type { PullRequest } from 'types/pullRequest'
import CardDetailsPage from 'components/CardDetailsPage'

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div data-testid="mock-tooltip" title={content}>
      {children}
    </div>
  ),
}))

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    fill,
    objectFit,
    ...props
  }: {
    src: string
    alt: string
    fill?: boolean
    objectFit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
    [key: string]: unknown
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      style={fill && { objectFit: objectFit as React.CSSProperties['objectFit'] }}
      {...props}
    />
  ),
}))

jest.mock('utils/env.client', () => ({
  IS_PROJECT_HEALTH_ENABLED: true,
}))

jest.mock('next-auth/react', () => {
  return {
    useSession: jest.fn(() => ({
      data: null,
      status: 'unauthenticated',
    })),
    SessionProvider: ({ children }: { children: React.ReactNode }) => children,
  }
})

jest.mock('utils/scrollToAnchor', () => ({
  scrollToAnchor: jest.fn(),
}))

jest.mock('utils/dateFormatter', () => ({
  formatDate: (date: string | number) => {
    if (typeof date === 'string') return date
    return new Date(date).toISOString().split('T')[0]
  },
}))

jest.mock('utils/urlFormatter', () => ({
  getMemberUrl: (login: string) => `/members/${login}`,
  getMenteeUrl: (programKey: string, entityKey: string, login: string) =>
    `/programs/${programKey}/mentees/${login}`,
}))

jest.mock('utils/urlIconMappings', () => ({
  getSocialIcon: (url: string) => {
    const safe = encodeURIComponent(url)
    return function MockSocialIcon(props: { className?: string }) {
      return <span data-testid={`mock-social-icon-${safe}`} className={props.className} />
    }
  },
}))

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({
    title,
    className,
    ...props
  }: {
    title: string
    className?: string
    [key: string]: unknown
  }) => (
    <span className={className} data-testid="anchor-title" {...props}>
      {title}
    </span>
  ),
}))

jest.mock('components/ChapterMapWrapper', () => ({
  __esModule: true,
  default: ({
    geoLocData: _geoLocData,
    showLocal,
    style,
    showLocationSharing: _showLocationSharing,
    ...otherProps
  }: {
    geoLocData?: unknown
    showLocal: boolean
    style: React.CSSProperties
    showLocationSharing?: boolean
    [key: string]: unknown
  }) => {
    return (
      <div data-testid="chapter-map-wrapper" style={style} {...otherProps}>
        Chapter Map {showLocal ? '(Local)' : ''}
      </div>
    )
  },
}))

jest.mock('components/HealthMetrics', () => ({
  __esModule: true,
  default: ({ data, ...props }: { data: unknown[]; [key: string]: unknown }) => (
    <div data-testid="health-metrics" {...props}>
      Health Metrics ({data.length} items)
    </div>
  ),
}))

jest.mock('components/ContributionHeatmap', () => ({
  __esModule: true,
  default: ({
    contributionData,
    startDate,
    endDate,
    ...props
  }: {
    contributionData: Record<string, number>
    startDate: string
    endDate: string
    [key: string]: unknown
  }) => (
    <div data-testid="mock-heatmap-chart" {...props}>
      Heatmap: {Object.keys(contributionData).length} days from {startDate} to {endDate}
    </div>
  ),
}))

jest.mock('components/ContributionStats', () => ({
  __esModule: true,
  default: ({
    title,
    stats,
    ...props
  }: {
    title: string
    stats?: { commits: number; pullRequests: number; issues: number; total: number }
    [key: string]: unknown
  }) => (
    <div data-testid="contribution-stats" {...props}>
      <h2>{title}</h2>
      {stats && (
        <>
          <p>Commits: {stats.commits}</p>
          <p>PRs: {stats.pullRequests}</p>
          <p>Issues: {stats.issues}</p>
        </>
      )}
    </div>
  ),
}))

jest.mock('components/InfoBlock', () => ({
  __esModule: true,
  default: ({
    icon: _icon,
    pluralizedName,
    unit,
    value,
    className,
    ...props
  }: {
    _icon: unknown
    pluralizedName?: string
    unit?: string
    value: number
    className?: string
    [key: string]: unknown
  }) => (
    <div data-testid="info-block" className={className} {...props}>
      {value} {unit} {pluralizedName}
    </div>
  ),
}))

jest.mock('components/LeadersList', () => ({
  __esModule: true,
  default: ({
    leaders,
    entityKey: _entityKey,
    ...props
  }: {
    leaders: string
    entityKey: string
    [key: string]: unknown
  }) => (
    <span data-testid="leaders-list" {...props}>
      {leaders}
    </span>
  ),
}))

jest.mock('components/MetricsScoreCircle', () => ({
  __esModule: true,
  default: ({
    score,
    clickable,
    onClick: _onClick,
    ...props
  }: {
    score: number
    clickable?: boolean
    onClick?: () => void
    [key: string]: unknown
  }) =>
    clickable ? (
      <button data-testid="metrics-score-circle" onClick={_onClick} {...props}>
        Score: {score}
      </button>
    ) : (
      <div data-testid="metrics-score-circle" {...props}>
        Score: {score}
      </div>
    ),
}))

jest.mock('components/Milestones', () => ({
  __esModule: true,
  default: ({
    data,
    showAvatar,
    ...props
  }: {
    data: unknown[]
    showAvatar: boolean
    [key: string]: unknown
  }) => (
    <div data-testid="milestones" {...props}>
      Milestones ({data?.length || 0} items) {showAvatar ? 'with avatars' : 'no avatars'}
    </div>
  ),
}))

jest.mock('components/RecentIssues', () => ({
  __esModule: true,
  default: ({
    data,
    showAvatar,
    ...props
  }: {
    data: unknown[]
    showAvatar: boolean
    [key: string]: unknown
  }) => (
    <div data-testid="recent-issues" {...props}>
      Recent Issues ({data?.length || 0} items) {showAvatar ? 'with avatars' : 'no avatars'}
    </div>
  ),
}))

jest.mock('components/RecentPullRequests', () => ({
  __esModule: true,
  default: ({
    data,
    showAvatar,
    ...props
  }: {
    data: unknown[]
    showAvatar: boolean
    [key: string]: unknown
  }) => (
    <div data-testid="recent-pull-requests" {...props}>
      Recent Pull Requests ({data?.length || 0} items) {showAvatar ? 'with avatars' : 'no avatars'}
    </div>
  ),
}))

jest.mock('components/MentorshipPullRequest', () => ({
  __esModule: true,
  default: ({ pr, ...props }: { pr: PullRequest; [key: string]: unknown }) => (
    <div data-testid="pull-request-item" {...props}>
      MentorshipPullRequest: {pr.title}
    </div>
  ),
}))

jest.mock('components/RecentReleases', () => ({
  __esModule: true,
  default: ({
    data,
    showAvatar,
    showSingleColumn,
    ...props
  }: {
    data: unknown[]
    showAvatar: boolean
    showSingleColumn?: boolean
    [key: string]: unknown
  }) => (
    <div data-testid="recent-releases" {...props}>
      Recent Releases ({data?.length || 0} items) {showAvatar ? 'with avatars' : 'no avatars'}
      {showSingleColumn ? ' (single column)' : ''}
    </div>
  ),
}))

jest.mock('components/RepositoryCard', () => ({
  __esModule: true,
  default: ({
    repositories,
    maxInitialDisplay: _maxInitialDisplay,
    ...props
  }: {
    repositories: unknown[]
    maxInitialDisplay?: number
    [key: string]: unknown
  }) => (
    <div data-testid="repositories-card" {...props}>
      Repositories ({repositories.length} items)
    </div>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({
    title,
    children,
    className,
    icon: _icon,
    ...props
  }: {
    _icon?: unknown
    title: React.ReactNode
    children: React.ReactNode
    className?: string
    [key: string]: unknown
  }) => (
    <div data-testid="secondary-card" className={className} {...props}>
      <h3>{title}</h3>
      <div>{children}</div>
    </div>
  ),
}))

jest.mock('components/SponsorCard', () => ({
  __esModule: true,
  default: ({
    target,
    title,
    type,
    ...props
  }: {
    target: string
    title: string
    type: string
    [key: string]: unknown
  }) => (
    <div data-testid="sponsor-card" {...props}>
      Sponsor Card - Target: {target}, Title: {title}, Type: {type}
    </div>
  ),
}))

jest.mock('components/ToggleableList', () => ({
  __esModule: true,
  default: ({
    items,
    icon: _icon,
    label,
    entityKey: _entityKey,
    isDisabled: _isDisabled,
    ...props
  }: {
    items: string[]
    _icon: unknown
    label: React.ReactNode
    entityKey: string
    isDisabled?: boolean
    [key: string]: unknown
  }) => (
    <div data-testid="toggleable-list" {...props}>
      {label}: {items.join(', ')}
    </div>
  ),
}))

jest.mock('components/ContributorsList', () => ({
  __esModule: true,
  default: ({
    contributors,
    maxInitialDisplay: _maxInitialDisplay,
    icon: _icon,
    title = 'Contributors',
    getUrl,
    ...props
  }: {
    contributors: (Partial<MenteeNode> & { tag?: string; login?: string; name?: string })[]
    icon?: unknown
    title?: string
    maxInitialDisplay: number
    getUrl: (login: string) => string
    [key: string]: unknown
  }) => (
    <div data-testid="contributors-list" {...props}>
      {title} ({contributors.length} items, max display: {_maxInitialDisplay})
      {contributors.map((c) => (
        <a key={c.tag || c.login || 'unknown'} href={getUrl && getUrl(c.login || 'unknown')}>
          {c.name || c.login || 'Unknown'}
        </a>
      ))}
    </div>
  ),
}))

jest.mock('components/EntityActions', () => ({
  __esModule: true,
  default: ({
    type,
    programKey,
    moduleKey,
    status: _status,
    setStatus: _setStatus,
    isAdmin,
    isMentor: _isMentor,
    ...props
  }: {
    type: string
    programKey?: string
    moduleKey?: string
    status?: string
    setStatus?: (status: string) => void
    isAdmin?: boolean
    isMentor?: boolean
    [key: string]: unknown
  }) => (
    <div data-testid="entity-actions" {...props} data-isadmin={isAdmin}>
      EntityActions: type={type}, programKey={programKey}, moduleKey={moduleKey}
    </div>
  ),
}))

jest.mock('components/Leaders', () => {
  return {
    __esModule: true,
    default: ({ users, ...props }: { users: unknown[]; [key: string]: unknown }) => {
      const usersList = users as Array<Record<string, unknown>>
      return (
        <div data-testid="leaders" {...props}>
          Leaders
          {Array.isArray(usersList) &&
            usersList.map((user: Record<string, unknown>) => (
              <div key={(user.id as string) || (user.name as string) || 'unknown'}>
                {(user.name as string) || 'Unknown'}
              </div>
            ))}
        </div>
      )
    },
  }
})

jest.mock('components/StatusBadge', () => ({
  __esModule: true,
  default: ({
    status,
    _size,
    ...props
  }: {
    status: string
    _size?: string
    [key: string]: unknown
  }) => (
    <span
      className={`px-3 py-1 text-sm ${status === 'inactive' ? 'bg-red-50 text-red-800' : 'bg-gray-300 text-gray-800'}`}
      data-testid={`status-badge-${status}`}
      {...props}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  ),
}))

jest.mock('components/MarkdownWrapper', () => ({
  __esModule: true,
  default: ({ content, ...props }: { content: string; [key: string]: unknown }) => (
    <div data-testid="markdown-wrapper" {...props}>
      {content}
    </div>
  ),
}))

jest.mock('components/ModuleCard', () => ({
  __esModule: true,
  default: ({
    modules,
    accessLevel: _accessLevel,
    admins: _admins,
    programKey: _programKey,
    ...props
  }: {
    modules: unknown[]
    accessLevel: string
    admins?: unknown[]
    programKey?: string
    [key: string]: unknown
  }) => (
    <div data-testid="module-card" {...props}>
      ModuleCard ({modules?.length || 0} modules)
    </div>
  ),
}))

jest.mock('components/ShowMoreButton', () => {
  function ShowMoreButtonMock({
    onToggle,
    ...props
  }: Readonly<{
    onToggle: () => void
    [key: string]: unknown
  }>) {
    const [isExpanded, setIsExpanded] = React.useState(false)
    return (
      <button
        onClick={() => {
          setIsExpanded(!isExpanded)
          onToggle()
        }}
        {...props}
      >
        {isExpanded ? 'Show less' : 'Show more'}
      </button>
    )
  }
  return {
    __esModule: true,
    default: ShowMoreButtonMock,
  }
})

jest.mock('components/TruncatedText', () => ({
  __esModule: true,
  TruncatedText: ({ text }: { text: string }) => <span>{text}</span>,
}))

describe('CardDetailsPage Integration Tests', () => {
  const mockHealthMetricsData = [
    {
      ageDays: 365,
      ageDaysRequirement: 365,
      id: 'test-id',
      createdAt: '2023-01-01',
      contributorsCount: 10,
      forksCount: 5,
      isFundingRequirementsCompliant: true,
      isLeaderRequirementsCompliant: true,
      lastCommitDays: 1,
      lastCommitDaysRequirement: 30,
      lastPullRequestDays: 2,
      lastPullRequestDaysRequirement: 30,
      lastReleaseDays: 10,
      lastReleaseDaysRequirement: 90,
      openIssuesCount: 5,
      openPullRequestsCount: 3,
      owaspPageLastUpdateDays: 30,
      owaspPageLastUpdateDaysRequirement: 90,
      projectName: 'Test Project',
      projectKey: 'test-project',
      recentReleasesCount: 2,
      score: 85,
      starsCount: 100,
      totalIssuesCount: 20,
      totalReleasesCount: 5,
      unassignedIssuesCount: 2,
      unansweredIssuesCount: 1,
    },
  ]

  const mockStats = [
    {
      icon: FaCode,
      pluralizedName: 'repositories',
      unit: '',
      value: 10,
    },
    {
      icon: FaTags,
      pluralizedName: 'stars',
      unit: '',
      value: 100,
    },
  ]

  const mockDetails = [
    { label: 'Created', value: '2023-01-01' },
    { label: 'Leaders', value: 'John Doe, Jane Smith' },
    { label: 'Status', value: 'Active' },
  ]

  const mockContributors = [
    {
      id: 'contributor-1',
      avatarUrl: 'https://example.com/avatar1.jpg',
      login: 'john_doe',
      name: 'John Doe',
      projectKey: 'test-project',
      contributionsCount: 50,
    },
    {
      id: 'contributor-2',
      avatarUrl: 'https://example.com/avatar2.jpg',
      login: 'jane_smith',
      name: 'Jane Smith',
      projectKey: 'test-project',
      contributionsCount: 30,
    },
  ]

  const mockRepositories = [
    {
      contributorsCount: 5,
      forksCount: 10,
      name: 'test-repo-1',
      openIssuesCount: 3,
      starsCount: 50,
      subscribersCount: 20,
      url: 'https://github.com/test/repo1',
      key: 'test-repo-1',
    },
    {
      contributorsCount: 8,
      forksCount: 15,
      name: 'test-repo-2',
      openIssuesCount: 5,
      starsCount: 80,
      subscribersCount: 30,
      url: 'https://github.com/test/repo2',
      key: 'test-repo-2',
    },
  ]

  const defaultProps: DetailsCardProps = {
    title: 'Test Project',
    description: 'A test project for demonstration',
    type: 'project',
    details: mockDetails,
    stats: mockStats,
    isActive: true,
    showAvatar: true,
    languages: ['JavaScript', 'TypeScript'],
    topics: ['web', 'frontend'],
    repositories: [],
    recentIssues: [],
    recentMilestones: [],
    recentReleases: [],
    pullRequests: [],
    topContributors: [],
    healthMetricsData: mockHealthMetricsData,
    socialLinks: [],
  }

  afterEach(() => {
    cleanup()
    jest.clearAllMocks()
  })

  describe('Essential Rendering Tests', () => {
    it('renders with all props provided', () => {
      render(<CardDetailsPage {...defaultProps} />)
      expect(screen.getByText('Test Project')).toBeInTheDocument()
      expect(screen.getByText('A test project for demonstration')).toBeInTheDocument()
    })
  })

  describe('Conditional Rendering by Type', () => {
    it('renders chapter map only for chapter type', () => {
      const chapterGeoData = [
        {
          createdAt: Date.now() - 31536000000,
          isActive: true,
          key: 'test-chapter',
          leaders: ['John Doe'],
          name: 'Test Chapter',
          objectID: 'chapter-test',
          region: 'North America',
          relatedUrls: ['https://example.com'],
          suggestedLocation: 'New York, NY',
          summary: 'Test chapter summary',
          topContributors: mockContributors,
          updatedAt: Date.now(),
          url: 'https://owasp.org/test-chapter',
          _geoloc: { lat: 40.7128, lng: -74.006 },
        },
      ]

      render(<CardDetailsPage {...defaultProps} type="chapter" geolocationData={chapterGeoData} />)
      expect(screen.getByTestId('chapter-map-wrapper')).toBeInTheDocument()
    })
  })

  describe('Contribution Data Handling', () => {
    it('detects contributions from contributionStats.total', () => {
      const propsWithContributionStats = {
        ...defaultProps,
        contributionStats: { total: 50, commits: 20, pullRequests: 15, issues: 15 },
        contributionData: undefined,
      }
      render(<CardDetailsPage {...propsWithContributionStats} />)
      expect(screen.getByTestId('contribution-stats')).toBeInTheDocument()
    })

    it('detects contributions from contributionData', () => {
      const propsWithContributionData = {
        ...defaultProps,
        contributionData: { '2023-01-01': 10, '2023-01-02': 5 },
        contributionStats: undefined,
        startDate: '2023-01-01',
        endDate: '2023-01-02',
      }
      render(<CardDetailsPage {...propsWithContributionData} />)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })
  })

  describe('Entity Leaders Rendering', () => {
    it('renders entity leaders when provided', () => {
      const leadersMock = [
        { name: 'Leader One', id: '1' },
        { name: 'Leader Two', id: '2' },
      ]
      render(<CardDetailsPage {...defaultProps} entityLeaders={leadersMock} />)
      expect(screen.getByTestId('leaders')).toBeInTheDocument()
      expect(screen.getByText('Leader One')).toBeInTheDocument()
      expect(screen.getByText('Leader Two')).toBeInTheDocument()
    })
  })

  describe('Health Metrics Conditional Rendering', () => {
    it('renders health metrics for project type with enabled flag', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="project"
          healthMetricsData={mockHealthMetricsData}
        />
      )
      expect(screen.getByTestId('health-metrics')).toBeInTheDocument()
    })

    it('does not render health metrics for non-project type', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="repository"
          healthMetricsData={mockHealthMetricsData}
        />
      )
      expect(screen.queryByTestId('health-metrics')).not.toBeInTheDocument()
    })
  })

  describe('SponsorCard Conditional Rendering', () => {
    it('renders sponsor card for chapter type with entityKey', () => {
      render(<CardDetailsPage {...defaultProps} type="chapter" entityKey="test-chapter" />)
      expect(screen.getByTestId('sponsor-card')).toBeInTheDocument()
    })

    it('uses projectName for sponsor card when available', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="chapter"
          entityKey="test-chapter"
          title="Component Title"
          projectName="Project Name"
        />
      )
      expect(screen.getByTestId('sponsor-card')).toBeInTheDocument()
      expect(screen.getByText(/Project Name/)).toBeInTheDocument()
    })
  })

  describe('Complex Branch Coverage', () => {
    it('renders all components with full data on project type', () => {
      const complexProps: DetailsCardProps = {
        ...defaultProps,
        title: 'Complex Project',
        type: 'project',
        entityKey: 'complex-project',
        entityLeaders: [{ name: 'Lead Dev', id: 'lead-1' }],
        contributionStats: {
          total: 100,
          commits: 50,
          pullRequests: 30,
          issues: 20,
        },
        topContributors: mockContributors,
        repositories: mockRepositories,
        recentIssues: [
          {
            title: 'Issue 1',
            url: 'https://github.com/issue1',
            createdAt: new Date().toISOString(),
            avatarUrl: 'https://example.com/avatar.jpg',
            name: 'Issue Reporter',
            type: 'Issue',
          },
        ],
        healthMetricsData: mockHealthMetricsData,
        projectName: 'Complex Project',
      }

      render(<CardDetailsPage {...complexProps} />)

      expect(screen.getByText('Complex Project')).toBeInTheDocument()
      expect(screen.getByTestId('leaders')).toBeInTheDocument()
      expect(screen.getByTestId('contributors-list')).toBeInTheDocument()
      expect(screen.getByTestId('repositories-card')).toBeInTheDocument()
      expect(screen.getByTestId('health-metrics')).toBeInTheDocument()
      expect(screen.getByTestId('sponsor-card')).toBeInTheDocument()
    })
  })
})
