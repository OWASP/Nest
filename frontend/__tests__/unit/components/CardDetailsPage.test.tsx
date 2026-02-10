import { render, screen, cleanup, fireEvent } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { FaCode, FaTags } from 'react-icons/fa6'
import type { DetailsCardProps } from 'types/card'
import type { PullRequest } from 'types/pullRequest'
import CardDetailsPage, { type CardType } from 'components/CardDetailsPage'

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
          <p>{stats.commits}</p>
          <p>{stats.pullRequests}</p>
          <p>{stats.issues}</p>
          <p>{stats.total}</p>
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
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    maxInitialDisplay,
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
    maxInitialDisplay,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    icon,
    title = 'Contributors',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    getUrl,
    ...props
  }: {
    contributors: unknown[]
    icon?: unknown
    title?: string
    maxInitialDisplay: number
    getUrl: (login: string) => string
    [key: string]: unknown
  }) => (
    <div data-testid="contributors-list" {...props}>
      {title} ({contributors.length} items, max display: {maxInitialDisplay})
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
    ...props
  }: {
    type: string
    programKey?: string
    moduleKey?: string
    status?: string
    setStatus?: (status: string) => void
    [key: string]: unknown
  }) => (
    <div data-testid="entity-actions" {...props}>
      EntityActions: type={type}, programKey={programKey}, moduleKey={moduleKey}
    </div>
  ),
}))

jest.mock('components/Leaders', () => {
  return {
    __esModule: true,
    default: ({ users, ...props }: { users: unknown[]; [key: string]: unknown }) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const usersList = users as any[]
      return (
        <div data-testid="leaders" {...props}>
          <h3>Leaders</h3>
          {Array.isArray(usersList) &&
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            usersList.map((user: any, index: number) => {
              const uniqueKey = `leader-${index}-${user.login || 'unknown'}`
              return (
                <div key={uniqueKey}>
                  <div>{user.member?.name || user.memberName || 'Unknown'}</div>
                  <div>{user.description || ''}</div>
                </div>
              )
            })}
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
    ...props
  }: {
    modules: unknown[]
    accessLevel: string
    admins?: unknown[]
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

describe('CardDetailsPage', () => {
  const createMalformedData = <T extends Record<string, unknown>>(
    validData: T,
    overrides: Record<string, unknown>
  ): T => {
    return { ...validData, ...overrides }
  }

  const createMalformedArray = <T extends Record<string, unknown>>(
    validArray: T[],
    malformedItems: Record<string, unknown>[]
  ): T[] => {
    return malformedItems.map((item, index) =>
      createMalformedData(validArray[index] || validArray[0], item)
    )
  }

  const createInvalidValues = () => ({
    nullValue: null,
    undefinedValue: undefined,
    emptyString: '',
    negativeNumber: -10,
    invalidUrl: 'not-a-url',
  })

  const invalidValues = createInvalidValues()

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

  const mockUser = {
    avatarUrl: 'https://example.com/avatar.jpg',
    contributionsCount: 100,
    createdAt: Date.now() - 31536000000,
    followersCount: 50,
    followingCount: 25,
    key: 'test-user',
    login: 'test_user',
    name: 'Test User',
    publicRepositoriesCount: 10,
    url: 'https://github.com/test_user',
  }

  const mockRecentIssues = [
    {
      author: mockUser,
      createdAt: Date.now() - 86400000,
      hint: 'Bug fix needed',
      labels: ['bug', 'high-priority'],
      number: '123',
      organizationName: 'test-org',
      projectName: 'Test Project',
      projectUrl: 'https://github.com/test/project',
      body: 'Issue summary',
      title: 'Test Issue',
      updatedAt: Date.now(),
      url: 'https://github.com/test/project/issues/123',
      objectID: 'issue-123',
    },
  ]

  const mockRecentMilestones = [
    {
      author: mockUser,
      body: 'Milestone description',
      closedIssuesCount: 5,
      createdAt: new Date(Date.now() - 2592000000).toISOString(),
      openIssuesCount: 2,
      repositoryName: 'test-repo',
      state: 'open',
      title: 'v1.0.0 Release',
      url: 'https://github.com/test/project/milestone/1',
    },
  ]

  const mockPullRequests = [
    {
      id: 'mock-pull-request-1',
      author: mockUser,
      createdAt: new Date(Date.now() - 172800000).toISOString(),
      organizationName: 'test-org',
      title: 'Add new feature',
      url: 'https://github.com/test/project/pull/456',
      state: 'merged',
      mergedAt: new Date(Date.now() - 86400000).toISOString(),
    },
  ]

  const mockRecentReleases = [
    {
      id: 'release-1',
      author: mockUser,
      isPreRelease: false,
      name: 'v1.0.0',
      publishedAt: Date.now() - 604800000,
      repositoryName: 'test-repo',
      tagName: 'v1.0.0',
      url: 'https://github.com/test/repo/releases/tag/v1.0.0',
    },
  ]

  const mockChapterGeoData = [
    {
      createdAt: Date.now() - 31536000000,
      isActive: true,
      key: 'test-chapter',
      leaders: ['John Doe', 'Jane Smith'],
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
    it('renders successfully with minimal required props', () => {
      const minimalProps: DetailsCardProps = {
        title: 'Minimal Project',
        type: 'project',
        stats: [],
        healthMetricsData: [],
        languages: [],
        topics: [],
      }

      render(<CardDetailsPage {...minimalProps} />)

      expect(screen.getByText('Minimal Project')).toBeInTheDocument()
      expect(screen.getByText('Project Details')).toBeInTheDocument()
    })

    it('renders with all props provided', () => {
      render(<CardDetailsPage {...defaultProps} />)

      expect(screen.getByText('Test Project')).toBeInTheDocument()
      expect(screen.getByText('A test project for demonstration')).toBeInTheDocument()
      expect(screen.getByText('Project Details')).toBeInTheDocument()
      expect(screen.getByText('Statistics')).toBeInTheDocument()
    })
  })

  describe('Conditional Rendering Logic', () => {
    it('renders inactive badge when isActive is false', () => {
      render(<CardDetailsPage {...defaultProps} isActive={false} />)

      expect(screen.getByText('Inactive')).toBeInTheDocument()
      // Updated classes for consistent badge styling.
      expect(screen.getByText('Inactive')).toHaveClass('bg-red-50', 'text-red-800')
    })

    it('does not render inactive badge when isActive is true', () => {
      render(<CardDetailsPage {...defaultProps} isActive={true} />)

      expect(screen.queryByText('Inactive')).not.toBeInTheDocument()
    })

    it('renders summary section when summary prop is provided', () => {
      render(<CardDetailsPage {...defaultProps} summary="This is a project summary" />)

      expect(screen.getByText('Summary')).toBeInTheDocument()
      expect(screen.getByText('This is a project summary')).toBeInTheDocument()
    })

    it('renders userSummary section when userSummary prop is provided', () => {
      const userSummary = <div>Custom user summary content</div>
      render(<CardDetailsPage {...defaultProps} userSummary={userSummary} />)

      const userSummaryContent = screen.getByText('Custom user summary content')
      expect(userSummaryContent).toBeInTheDocument()
    })

    it('renders health metrics when type is project and health data is available', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="project"
          healthMetricsData={mockHealthMetricsData}
        />
      )

      expect(screen.getByTestId('health-metrics')).toBeInTheDocument()
      expect(screen.getByTestId('metrics-score-circle')).toBeInTheDocument()
    })

    it('does not render health metrics when type is not project', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="repository"
          healthMetricsData={mockHealthMetricsData}
        />
      )

      expect(screen.queryByTestId('health-metrics')).not.toBeInTheDocument()
    })

    it('renders chapter map when type is chapter and geolocation data is provided', () => {
      render(
        <CardDetailsPage {...defaultProps} type="chapter" geolocationData={mockChapterGeoData} />
      )

      expect(screen.getByTestId('chapter-map-wrapper')).toBeInTheDocument()
    })

    it('renders social links for chapter and committee types', () => {
      const socialLinks = ['https://github.com/test', 'https://twitter.com/test']
      render(<CardDetailsPage {...defaultProps} type="chapter" socialLinks={socialLinks} />)

      expect(screen.getByText('Social Links')).toBeInTheDocument()
      expect(screen.getAllByRole('link')).toHaveLength(2)
    })
  })

  describe('Prop-based Behavior', () => {
    it('renders different grid layout for chapter type', () => {
      render(<CardDetailsPage {...defaultProps} type="chapter" />)

      const detailsCard = screen.getByTestId('secondary-card')
      expect(detailsCard).toHaveClass('md:col-span-3')
    })

    it('renders different grid layout for non-chapter types', () => {
      render(<CardDetailsPage {...defaultProps} type="project" />)

      const detailsCards = screen.getAllByTestId('secondary-card')
      const detailsCard = detailsCards.find((card) => card.textContent?.includes('Project Details'))
      expect(detailsCard).toHaveClass('md:col-span-5')
    })

    const supportedTypes: CardType[] = [
      'project',
      'repository',
      'committee',
      'user',
      'organization',
    ]

    test.each(supportedTypes)('renders statistics section for %s type', (entityType) => {
      render(<CardDetailsPage {...defaultProps} type={entityType} />)
      expect(screen.getByText('Statistics')).toBeInTheDocument()
    })

    it('renders languages and topics for project and repository types', () => {
      render(<CardDetailsPage {...defaultProps} type="project" />)

      expect(screen.getAllByTestId('toggleable-list')).toHaveLength(2)
      expect(
        screen.getByText(
          (content, element) => element?.textContent === 'Languages: JavaScript, TypeScript'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByText((content, element) => element?.textContent === 'Topics: web, frontend')
      ).toBeInTheDocument()
    })

    it('renders repositories section when repositories are provided', () => {
      render(<CardDetailsPage {...defaultProps} repositories={mockRepositories} />)

      expect(screen.getByText('Repositories')).toBeInTheDocument()
      expect(screen.getByTestId('repositories-card')).toBeInTheDocument()
    })

    it('renders MentorshipPullRequest when type is module and PRs are provided', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="module"
          pullRequests={mockPullRequests as unknown as PullRequest[]}
        />
      )

      expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
      expect(screen.getAllByTestId('pull-request-item').length).toBeGreaterThan(0)
    })
  })

  describe('Event Handling', () => {
    it('renders clickable health metrics button', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="project"
          healthMetricsData={mockHealthMetricsData}
        />
      )

      const healthButton = screen.getByRole('button')
      expect(healthButton).toBeInTheDocument()
      expect(screen.getByTestId('metrics-score-circle')).toBeInTheDocument()
    })

    it('calls scrollToAnchor when MetricsScoreCircle is clicked', () => {
      const { scrollToAnchor } = jest.requireMock('utils/scrollToAnchor')

      render(
        <CardDetailsPage
          {...defaultProps}
          type="project"
          healthMetricsData={mockHealthMetricsData}
        />
      )

      const healthButton = screen.getByRole('button')
      fireEvent.click(healthButton)

      expect(scrollToAnchor).toHaveBeenCalledWith('issues-trend')
    })

    it('renders social links with correct hrefs and target attributes', () => {
      const socialLinks = ['https://github.com/test', 'https://twitter.com/test']
      render(<CardDetailsPage {...defaultProps} type="chapter" socialLinks={socialLinks} />)

      const links = screen.getAllByRole('link')
      for (const link of links) {
        expect(link).toHaveAttribute('target', '_blank')
        expect(link).toHaveAttribute('rel', 'noopener noreferrer')
      }
    })
  })

  describe('Text and Content Rendering', () => {
    it('renders title correctly', () => {
      render(<CardDetailsPage {...defaultProps} title="Custom Project Title" />)

      expect(screen.getByText('Custom Project Title')).toBeInTheDocument()
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Custom Project Title')
    })

    it('renders description correctly', () => {
      render(<CardDetailsPage {...defaultProps} description="Custom project description" />)

      expect(screen.getByText('Custom project description')).toBeInTheDocument()
    })

    it('renders details with proper formatting', () => {
      render(<CardDetailsPage {...defaultProps} />)

      expect(screen.getByText('Created:')).toBeInTheDocument()
      expect(screen.getByText('2023-01-01')).toBeInTheDocument()
      expect(screen.getByText('Status:')).toBeInTheDocument()
      expect(screen.getByText('Active')).toBeInTheDocument()
    })

    it('renders leaders with special formatting', () => {
      render(<CardDetailsPage {...defaultProps} />)

      expect(screen.getByText('Leaders:')).toBeInTheDocument()
      expect(screen.getByTestId('leaders-list')).toBeInTheDocument()
    })

    it('renders Leaders component when entityLeaders are provided', () => {
      const entityLeaders = [
        {
          description: 'Project Leader',
          memberName: 'Alice',
          member: {
            id: '1',
            login: 'alice',
            name: 'Alice',
            avatarUrl: 'https://avatars.githubusercontent.com/u/12345?v=4',
          },
        },
      ]
      render(<CardDetailsPage {...defaultProps} entityLeaders={entityLeaders} />)
      expect(screen.getByText('Leaders')).toBeInTheDocument()
      expect(screen.getByText('Alice')).toBeInTheDocument()
      expect(screen.getByText('Project Leader')).toBeInTheDocument()
    })

    it('capitalizes entity type in details title', () => {
      render(<CardDetailsPage {...defaultProps} type="project" />)

      expect(screen.getByText('Project Details')).toBeInTheDocument()
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('handles missing title gracefully', () => {
      render(<CardDetailsPage {...defaultProps} title={undefined} />)

      expect(screen.queryByRole('heading', { level: 1 })).toBeInTheDocument()
    })

    it('handles empty details array', () => {
      render(<CardDetailsPage {...defaultProps} details={[]} />)

      expect(screen.getByText('Project Details')).toBeInTheDocument()
    })

    it('handles empty stats array', () => {
      render(<CardDetailsPage {...defaultProps} stats={[]} />)

      expect(screen.getByText('Statistics')).toBeInTheDocument()
    })

    it('handles missing detail values with fallback', () => {
      const detailsWithMissingValues = [
        { label: 'Missing Value', value: invalidValues.emptyString },
        { label: 'Null Value', value: invalidValues.nullValue },
        { label: 'Undefined Value', value: invalidValues.undefinedValue },
      ]

      render(<CardDetailsPage {...defaultProps} details={detailsWithMissingValues} />)

      expect(screen.getAllByText('Unknown')).toHaveLength(3)
    })

    it('handles empty languages and topics arrays', () => {
      render(<CardDetailsPage {...defaultProps} languages={[]} topics={[]} />)

      expect(screen.queryByText('Languages:')).not.toBeInTheDocument()
      expect(screen.queryByText('Topics:')).not.toBeInTheDocument()
    })

    it('handles empty social links array', () => {
      render(<CardDetailsPage {...defaultProps} type="chapter" socialLinks={[]} />)

      expect(screen.queryByText('Social Links')).not.toBeInTheDocument()
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('uses default isActive value when not provided', () => {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { isActive, ...propsWithoutIsActive } = defaultProps

      render(<CardDetailsPage {...propsWithoutIsActive} />)

      expect(screen.queryByText('Inactive')).not.toBeInTheDocument()
    })

    it('uses default showAvatar value when not provided', () => {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { showAvatar, ...propsWithoutShowAvatar } = defaultProps

      render(<CardDetailsPage {...propsWithoutShowAvatar} />)

      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    it('uses default geolocationData value when not provided', () => {
      render(<CardDetailsPage {...defaultProps} type="chapter" />)

      expect(screen.queryByTestId('chapter-map-wrapper')).not.toBeInTheDocument()
    })
  })

  describe('DOM Structure and Styling', () => {
    it('applies correct CSS classes to main container', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const mainContainer = document.querySelector('.min-h-screen')
      expect(mainContainer).toHaveClass(
        'min-h-screen',
        'bg-white',
        'p-8',
        'text-gray-600',
        'dark:bg-[#212529]',
        'dark:text-gray-300'
      )
    })

    it('applies correct CSS classes to title', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const title = screen.getByRole('heading', { level: 1 })
      expect(title).toHaveClass('text-4xl', 'font-bold')
    })

    it('applies correct CSS classes to description', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const description = screen.getByText('A test project for demonstration')
      expect(description).toHaveClass('mb-6', 'text-xl')
    })

    it('applies correct grid classes based on content', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const gridContainer = screen.getByText('Project Details').closest('div')?.parentElement
      expect(gridContainer).toHaveClass('grid', 'grid-cols-1', 'gap-6', 'md:grid-cols-7')
    })
  })

  describe('Component Integration', () => {
    it('passes correct props to child components', () => {
      render(<CardDetailsPage {...defaultProps} topContributors={mockContributors} />)

      expect(screen.getByTestId('contributors-list')).toHaveTextContent(
        'Top Contributors (2 items, max display: 12)'
      )
    })

    it('renders sponsor card with correct props', () => {
      render(
        <CardDetailsPage {...defaultProps} entityKey="test-key" projectName="Test Project Name" />
      )

      expect(screen.getByTestId('sponsor-card')).toHaveTextContent(
        'Sponsor Card - Target: test-key, Title: Test Project Name, Type: project'
      )
    })

    it('renders recent components for supported types', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          recentIssues={mockRecentIssues}
          recentMilestones={mockRecentMilestones}
          pullRequests={mockPullRequests}
          recentReleases={mockRecentReleases}
        />
      )

      expect(screen.getByTestId('recent-issues')).toBeInTheDocument()
      expect(screen.getByTestId('milestones')).toBeInTheDocument()
      expect(screen.getByTestId('recent-pull-requests')).toBeInTheDocument()
      expect(screen.getByTestId('recent-releases')).toBeInTheDocument()
    })

    const entityTypes: CardType[] = [
      'project',
      'repository',
      'user',
      'organization',
      'committee',
      'chapter',
    ]

    test.each(entityTypes)('renders all expected sections for %s type', (entityType) => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type={entityType}
          geolocationData={entityType === 'chapter' ? mockChapterGeoData : undefined}
          socialLinks={
            ['chapter', 'committee'].includes(entityType) ? ['https://github.com/test'] : undefined
          }
        />
      )

      expect(
        screen.getByText(`${entityType.charAt(0).toUpperCase() + entityType.slice(1)} Details`)
      ).toBeInTheDocument()
    })

    const supportedTypes: CardType[] = [
      'project',
      'repository',
      'committee',
      'user',
      'organization',
    ]

    test.each(supportedTypes)('renders statistics section for supported %s type', (entityType) => {
      render(<CardDetailsPage {...defaultProps} type={entityType} />)
      expect(screen.getByText('Statistics')).toBeInTheDocument()
    })

    it('renders chapter map for chapter type only', () => {
      render(
        <CardDetailsPage {...defaultProps} type="chapter" geolocationData={mockChapterGeoData} />
      )

      expect(screen.getByTestId('chapter-map-wrapper')).toBeInTheDocument()
    })

    it('properly handles arrays vs single items in props', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          healthMetricsData={mockHealthMetricsData}
          topContributors={mockContributors}
          repositories={mockRepositories}
        />
      )

      expect(screen.getByTestId('health-metrics')).toHaveTextContent('Health Metrics (1 items)')
      expect(screen.getByTestId('contributors-list')).toHaveTextContent('Top Contributors (2 items')
      expect(screen.getByTestId('repositories-card')).toHaveTextContent('Repositories (2 items)')
    })

    it('handles conditional rendering based on array lengths', () => {
      render(<CardDetailsPage {...defaultProps} languages={['JavaScript']} topics={[]} />)

      expect(screen.getByTestId('toggleable-list')).toHaveTextContent('Languages: JavaScript')
      expect(screen.queryByText('Topics:')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility and Semantic HTML', () => {
    it('uses proper heading hierarchy', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const mainHeading = screen.getByRole('heading', { level: 1 })
      expect(mainHeading).toHaveTextContent('Test Project')

      const sectionHeadings = screen.getAllByRole('heading', { level: 3 })
      expect(sectionHeadings.length).toBeGreaterThan(0)
    })

    it('provides proper link attributes for external links', () => {
      const socialLinks = ['https://github.com/test', 'https://twitter.com/test']
      render(<CardDetailsPage {...defaultProps} type="chapter" socialLinks={socialLinks} />)

      const links = screen.getAllByRole('link')
      const externalLinks = links.filter((link) => link.getAttribute('href')?.startsWith('http'))

      for (const link of externalLinks) {
        expect(link).toHaveAttribute('target', '_blank')
        expect(link).toHaveAttribute('rel', 'noopener noreferrer')
      }
    })

    it('renders with proper document structure', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const mainContainer = document.querySelector('.min-h-screen')
      expect(mainContainer).toBeInTheDocument()

      const contentWrapper = document.querySelector('.mx-auto.max-w-6xl')
      expect(contentWrapper).toBeInTheDocument()
    })
  })

  describe('Responsive Design Classes', () => {
    it('applies responsive grid classes correctly', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const gridContainer = screen.getByText('Project Details').closest('div')?.parentElement
      expect(gridContainer).toHaveClass('grid', 'grid-cols-1', 'gap-6', 'md:grid-cols-7')
    })

    it('applies correct column spans for different layouts', () => {
      render(<CardDetailsPage {...defaultProps} type="chapter" />)
      const chapterDetailsCard = screen.getByTestId('secondary-card')
      expect(chapterDetailsCard).toHaveClass('md:col-span-3')

      cleanup()

      render(<CardDetailsPage {...defaultProps} type="project" />)
      const detailsCards = screen.getAllByTestId('secondary-card')
      const detailsCard = detailsCards.find((card) => card.textContent?.includes('Project Details'))
      expect(detailsCard).toHaveClass('md:col-span-5')
    })

    it('applies responsive classes to languages and topics section', () => {
      render(<CardDetailsPage {...defaultProps} languages={['JavaScript']} topics={['web']} />)

      const languagesTopicsContainer = screen
        .getAllByTestId('toggleable-list')[0]
        .closest('div')?.parentElement
      expect(languagesTopicsContainer).toHaveClass(
        'mb-8',
        'grid',
        'grid-cols-1',
        'gap-6',
        'md:grid-cols-2'
      )
    })
  })

  describe('Performance and Optimization', () => {
    it('does not render expensive components when not needed', () => {
      render(
        <CardDetailsPage
          {...defaultProps}
          type="repository"
          healthMetricsData={[]}
          topContributors={undefined}
          repositories={[]}
        />
      )

      expect(screen.queryByTestId('health-metrics')).not.toBeInTheDocument()
      expect(screen.queryByTestId('repositories-card')).not.toBeInTheDocument()
    })

    it('handles large arrays efficiently', () => {
      const largeContributorsList = Array.from({ length: 50 }, (_, i) => ({
        ...mockContributors[0],
        login: `contributor-${i}`,
        name: `Contributor ${i}`,
      }))

      render(<CardDetailsPage {...defaultProps} topContributors={largeContributorsList} />)

      expect(screen.getByTestId('contributors-list')).toHaveTextContent(
        'Top Contributors (50 items, max display: 12)'
      )
    })
  })

  describe('Data Validation and Error Handling', () => {
    it('handles malformed health metrics data gracefully', () => {
      const malformedHealthData = [
        createMalformedData(mockHealthMetricsData[0], { score: invalidValues.nullValue }),
      ]

      render(
        <CardDetailsPage {...defaultProps} type="project" healthMetricsData={malformedHealthData} />
      )

      expect(screen.getByTestId('health-metrics')).toBeInTheDocument()
      expect(screen.getByTestId('metrics-score-circle')).toBeInTheDocument()
    })

    it('handles invalid health metrics score gracefully', () => {
      const invalidHealthData = createMalformedArray(mockHealthMetricsData, [
        { score: invalidValues.negativeNumber },
        { score: invalidValues.undefinedValue },
      ])

      render(
        <CardDetailsPage {...defaultProps} type="project" healthMetricsData={invalidHealthData} />
      )

      expect(screen.getByTestId('health-metrics')).toBeInTheDocument()
    })

    it('handles invalid social link URLs gracefully', () => {
      const invalidSocialLinks = ['', 'not-a-url', 'invalid://url']

      expect(() =>
        render(
          <CardDetailsPage {...defaultProps} type="chapter" socialLinks={invalidSocialLinks} />
        )
      ).not.toThrow()

      expect(screen.getByText('Social Links')).toBeInTheDocument()
    })

    it('handles unsupported entity types gracefully', () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      render(<CardDetailsPage {...defaultProps} type={'unsupported-type' as any} />)
      expect(screen.getByText('Unsupported-type Details')).toBeInTheDocument()
    })

    it('handles extremely large contributor arrays', () => {
      const largeContributors = Array.from({ length: 1000 }, (_, i) => ({
        ...mockContributors[0],
        login: `user-${i}`,
        name: `User ${i}`,
      }))

      render(<CardDetailsPage {...defaultProps} topContributors={largeContributors} />)

      expect(screen.getByTestId('contributors-list')).toHaveTextContent(
        'Top Contributors (1000 items, max display: 12)'
      )
    })

    it('handles contributors with missing required fields', () => {
      const incompleteContributors = createMalformedArray(mockContributors, [
        {
          avatarUrl: invalidValues.emptyString,
          login: invalidValues.emptyString,
          name: invalidValues.emptyString,
          projectKey: 'project1',
        },
        {
          avatarUrl: 'https://example.com/avatar.jpg',
          login: 'user2',
          name: invalidValues.nullValue,
          projectKey: 'project1',
        },
      ])

      expect(() =>
        render(<CardDetailsPage {...defaultProps} topContributors={incompleteContributors} />)
      ).not.toThrow()
    })

    it('validates required vs optional props correctly', () => {
      const minimalValidProps: DetailsCardProps = {
        type: 'project' as const,
        stats: [],
        healthMetricsData: [],
        languages: [],
        topics: [],
      }

      expect(() => render(<CardDetailsPage {...minimalValidProps} />)).not.toThrow()
    })

    it('handles undefined and null values in arrays', () => {
      const propsWithUndefinedArrays = {
        ...defaultProps,
        recentIssues: undefined,
        recentMilestones: null,
        topContributors: undefined,
      }

      expect(() => render(<CardDetailsPage {...propsWithUndefinedArrays} />)).not.toThrow()
    })

    it('handles malformed repository data', () => {
      const malformedRepositories = createMalformedArray(mockRepositories, [
        {
          name: invalidValues.nullValue,
          contributorsCount: invalidValues.negativeNumber,
        },
        {
          url: invalidValues.emptyString,
          starsCount: invalidValues.undefinedValue,
        },
      ])

      expect(() =>
        render(<CardDetailsPage {...defaultProps} repositories={malformedRepositories} />)
      ).not.toThrow()
    })

    it('handles empty string values in details', () => {
      const detailsWithEmptyStrings = [
        { label: invalidValues.emptyString, value: 'Some Value' },
        { label: 'Some Label', value: invalidValues.emptyString },
        { label: invalidValues.nullValue, value: invalidValues.nullValue },
      ]

      expect(() =>
        render(<CardDetailsPage {...defaultProps} details={detailsWithEmptyStrings} />)
      ).not.toThrow()
    })
  })

  describe('Advanced Integration Tests', () => {
    it('handles multiple rapid prop changes', () => {
      const { rerender } = render(<CardDetailsPage {...defaultProps} type={'project' as const} />)

      rerender(<CardDetailsPage {...defaultProps} type={'chapter' as const} />)
      expect(screen.getByText('Chapter Details')).toBeInTheDocument()

      rerender(<CardDetailsPage {...defaultProps} type={'user' as const} />)
      expect(screen.getByText('User Details')).toBeInTheDocument()

      rerender(<CardDetailsPage {...defaultProps} type={'organization' as const} />)
      expect(screen.getByText('Organization Details')).toBeInTheDocument()
    })

    it('handles complex nested data structures', () => {
      const complexProps = {
        ...defaultProps,
        details: [
          {
            label: 'Complex Detail',
            value: (
              <div>
                <span>Nested</span> <strong>Content</strong>
              </div>
            ),
          },
        ],
        userSummary: (
          <div>
            <p>Complex user summary</p>
            <ul>
              <li>Item 1</li>
              <li>Item 2</li>
            </ul>
          </div>
        ),
      }

      render(<CardDetailsPage {...complexProps} />)

      expect(screen.getByText('Nested')).toBeInTheDocument()
      expect(screen.getByText('Content')).toBeInTheDocument()
      expect(screen.getByText('Complex user summary')).toBeInTheDocument()
      expect(screen.getByText('Item 1')).toBeInTheDocument()
      expect(screen.getByText('Item 2')).toBeInTheDocument()
    })

    it('renders correctly with all optional sections enabled', () => {
      const fullPropsAllSections: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        summary: 'Project summary text',
        userSummary: <div>User summary content</div>,
        socialLinks: ['https://github.com/test', 'https://twitter.com/test'],
        entityKey: 'test-entity',
        projectName: 'Test Project Name',
        geolocationData: mockChapterGeoData,
        healthMetricsData: mockHealthMetricsData,
        topContributors: mockContributors,
        repositories: mockRepositories,
        recentIssues: mockRecentIssues,
        recentMilestones: mockRecentMilestones,
        recentReleases: mockRecentReleases,
        pullRequests: mockPullRequests,
      }

      render(<CardDetailsPage {...fullPropsAllSections} />)

      expect(screen.getByText('Project summary text')).toBeInTheDocument()
      expect(screen.getByText('User summary content')).toBeInTheDocument()
      expect(screen.getByTestId('health-metrics')).toBeInTheDocument()
      expect(screen.getByTestId('contributors-list')).toBeInTheDocument()
      expect(screen.getByTestId('repositories-card')).toBeInTheDocument()
      expect(screen.getByTestId('sponsor-card')).toBeInTheDocument()
    })

    it('handles zero and negative values in stats', () => {
      const statsWithZeroValues = [
        { icon: FaCode, value: 0, unit: 'Star' },
        { icon: FaTags, value: -10, unit: 'Issue' },
        { icon: FaCode, value: null, unit: 'Fork' },
      ]

      expect(() =>
        render(<CardDetailsPage {...defaultProps} stats={statsWithZeroValues} />)
      ).not.toThrow()

      expect(screen.getByText('Statistics')).toBeInTheDocument()
    })

    it('handles mixed valid and invalid data in arrays', () => {
      const mixedValidInvalidData = {
        ...defaultProps,
        recentIssues: [
          mockRecentIssues[0], // Valid
          createMalformedData(mockRecentIssues[0], { title: invalidValues.nullValue }),
          createMalformedData(mockRecentIssues[0], { author: invalidValues.nullValue }),
        ],
        languages: ['JavaScript', invalidValues.emptyString, invalidValues.nullValue, 'TypeScript'],
        topics: ['web', invalidValues.undefinedValue, 'frontend', invalidValues.emptyString],
      }

      expect(() => render(<CardDetailsPage {...mixedValidInvalidData} />)).not.toThrow()
    })
  })

  describe('Accessibility Edge Cases', () => {
    it('maintains accessibility with missing aria labels', () => {
      render(<CardDetailsPage {...defaultProps} />)

      const h1 = screen.getByRole('heading', { level: 1 })
      expect(h1).toBeInTheDocument()

      const h3s = screen.getAllByRole('heading', { level: 3 })
      expect(h3s.length).toBeGreaterThan(0)
    })

    it('handles very long text content gracefully', () => {
      const longTextProps = {
        ...defaultProps,
        title: 'A'.repeat(500),
        description: 'B'.repeat(1000),
        summary: 'C'.repeat(2000),
      }

      render(<CardDetailsPage {...longTextProps} />)

      expect(screen.getByText('A'.repeat(500))).toBeInTheDocument()
      expect(screen.getByText('B'.repeat(1000))).toBeInTheDocument()
      expect(screen.getByText('C'.repeat(2000))).toBeInTheDocument()
    })

    it('handles special characters in text content', () => {
      const specialCharProps = {
        ...defaultProps,
        title: 'Project with "quotes" & <symbols>',
        description: 'Description with symbols 🚀 and special characters',
        details: [{ label: 'Special & Label', value: 'Value with <tags>' }],
      }

      render(<CardDetailsPage {...specialCharProps} />)

      expect(screen.getByText('Project with "quotes" & <symbols>')).toBeInTheDocument()
      expect(
        screen.getByText('Description with symbols 🚀 and special characters')
      ).toBeInTheDocument()
    })
  })

  describe('Archived Badge Functionality', () => {
    it('displays archived badge for archived repository', () => {
      const archivedProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        isArchived: true,
      }

      render(<CardDetailsPage {...archivedProps} />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
    })

    it('does not display archived badge for non-archived repository', () => {
      const activeProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        isArchived: false,
      }

      render(<CardDetailsPage {...activeProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('does not display archived badge when isArchived is undefined', () => {
      const undefinedProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
      }

      render(<CardDetailsPage {...undefinedProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('does not display archived badge for non-repository types', () => {
      const projectProps: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        isArchived: true,
      }

      render(<CardDetailsPage {...projectProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('displays archived badge alongside inactive badge', () => {
      const bothBadgesProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        isArchived: true,
        isActive: false,
      }

      render(<CardDetailsPage {...bothBadgesProps} />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
      expect(screen.getByText('Inactive')).toBeInTheDocument()
    })

    it('displays archived badge independently of active status', () => {
      const archivedAndActiveProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        isArchived: true,
        isActive: true,
      }

      render(<CardDetailsPage {...archivedAndActiveProps} />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
      expect(screen.queryByText('Inactive')).not.toBeInTheDocument()
    })

    it('archived badge has correct positioning with flex container', () => {
      const archivedProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        isArchived: true,
      }

      const { container } = render(<CardDetailsPage {...archivedProps} />)

      // New structure: badges are in a flex container with items-center and gap-3
      const badgeContainer = container.querySelector('.flex.items-center.gap-3')
      expect(badgeContainer).toBeInTheDocument()
    })

    it('archived badge renders with medium size', () => {
      const archivedProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        isArchived: true,
      }

      render(<CardDetailsPage {...archivedProps} />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-3', 'py-1', 'text-sm')
    })

    it('handles null isArchived gracefully', () => {
      const nullArchivedProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        isArchived: null,
      }

      render(<CardDetailsPage {...nullArchivedProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })
  })

  describe('Contribution Stats and Heatmap', () => {
    const contributionData = {
      '2024-01-01': 5,
      '2024-01-02': 10,
      '2024-01-03': 3,
    }

    const contributionStats = {
      commits: 100,
      pullRequests: 50,
      issues: 25,
      total: 175,
    }

    it('renders contribution stats and heatmap when data is provided', () => {
      const propsWithContributions: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        contributionData,
        contributionStats,
        startDate: '2024-01-01',
        endDate: '2024-12-31',
      }

      render(<CardDetailsPage {...propsWithContributions} />)

      expect(screen.getByText('Project Contribution Activity')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('50')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
      expect(screen.getByText('175')).toBeInTheDocument()
    })

    it('uses correct title for chapter type', () => {
      const chapterPropsWithContributions: DetailsCardProps = {
        ...defaultProps,
        type: 'chapter' as const,
        contributionStats,
      }

      render(<CardDetailsPage {...chapterPropsWithContributions} />)

      expect(screen.getByText('Chapter Contribution Activity')).toBeInTheDocument()
    })

    it('does not render contribution section when no data is provided', () => {
      render(<CardDetailsPage {...defaultProps} type={'project' as const} />)

      expect(screen.queryByText('Project Contribution Activity')).not.toBeInTheDocument()
      expect(screen.queryByText('Chapter Contribution Activity')).not.toBeInTheDocument()
    })

    it('renders only stats when contributionData is missing', () => {
      const statsOnlyProps: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        contributionStats,
      }

      render(<CardDetailsPage {...statsOnlyProps} />)

      expect(screen.getByText('Project Contribution Activity')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('renders heatmap when contributionData and dates are provided', () => {
      const heatmapProps: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        contributionData,
        startDate: '2024-01-01',
        endDate: '2024-12-31',
      }

      render(<CardDetailsPage {...heatmapProps} />)

      // Heatmap should be rendered (mocked in jest setup)
      expect(screen.getByTestId('mock-heatmap-chart')).toBeInTheDocument()
    })

    it('does not render heatmap when dates are missing', () => {
      const noDateProps: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        contributionData,
      }

      render(<CardDetailsPage {...noDateProps} />)

      expect(screen.queryByTestId('mock-heatmap-chart')).not.toBeInTheDocument()
    })

    it('does not render heatmap when contributionData is empty', () => {
      const emptyDataProps: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        contributionData: {},
        startDate: '2024-01-01',
        endDate: '2024-12-31',
      }

      render(<CardDetailsPage {...emptyDataProps} />)

      expect(screen.queryByTestId('mock-heatmap-chart')).not.toBeInTheDocument()
    })

    it('renders contribution section before top contributors', () => {
      const fullProps: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        contributionStats,
        topContributors: [
          {
            id: 'contributor-user1',
            login: 'user1',
            name: 'User One',
            avatarUrl: 'https://example.com/avatar1.png',
          },
        ],
      }

      render(<CardDetailsPage {...fullProps} />)

      const contributionSection = screen.getByText('Project Contribution Activity')
      const contributorsSection = screen.getByText(/Top Contributors/i)

      // Check that contribution section appears before contributors
      expect(contributionSection.compareDocumentPosition(contributorsSection)).toBe(
        Node.DOCUMENT_POSITION_FOLLOWING
      )
    })
  })

  describe('Program Milestones Display', () => {
    const createMilestones = (count: number) => {
      const milestones = []
      for (let i = 0; i < count; i++) {
        milestones.push({
          author: mockUser,
          body: `Milestone description ${i + 1}`,
          closedIssuesCount: 5,
          createdAt: new Date(Date.now() - 10000000).toISOString(),
          openIssuesCount: 2,
          repositoryName: `test-repo-${i}`,
          organizationName: 'test-org',
          state: 'open',
          title: `Milestone ${i + 1}`,
          url: `https://github.com/test/project/milestone/${i + 1}`,
        })
      }
      return milestones
    }

    it('renders only first 4 milestones initially for program type', () => {
      const manyMilestones = createMilestones(6)
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: manyMilestones,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText('Recent Milestones')).toBeInTheDocument()

      expect(screen.getByText('Milestone 1')).toBeInTheDocument()
      expect(screen.getByText('Milestone 4')).toBeInTheDocument()

      expect(screen.queryByText('Milestone 5')).not.toBeInTheDocument()
      expect(screen.queryByText('Milestone 6')).not.toBeInTheDocument()

      expect(screen.getByText(/Show more/i)).toBeInTheDocument()
    })

    it('expands to show all milestones when "Show more" is clicked', () => {
      const manyMilestones = createMilestones(6)
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: manyMilestones,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      const showMoreBtn = screen.getByText(/Show more/i)
      fireEvent.click(showMoreBtn)

      expect(screen.getByText('Milestone 5')).toBeInTheDocument()
      expect(screen.getByText('Milestone 6')).toBeInTheDocument()

      expect(screen.getByText(/Show less/i)).toBeInTheDocument()
    })

    it('collapses back to 4 milestones when "Show less" is clicked', () => {
      const manyMilestones = createMilestones(6)
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: manyMilestones,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      fireEvent.click(screen.getByText(/Show more/i))
      expect(screen.getByText('Milestone 5')).toBeInTheDocument()

      fireEvent.click(screen.getByText(/Show less/i))

      expect(screen.queryByText('Milestone 5')).not.toBeInTheDocument()
      expect(screen.getByText(/Show more/i)).toBeInTheDocument()
    })

    it('does not show toggle button if milestones <= 4', () => {
      const fewMilestones = createMilestones(4)
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: fewMilestones,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText('Milestone 1')).toBeInTheDocument()
      expect(screen.getByText('Milestone 4')).toBeInTheDocument()
      expect(screen.queryByText(/Show more/i)).not.toBeInTheDocument()
    })

    it('renders milestone author avatar when showAvatar is true and author data is complete', () => {
      const milestonesWithAuthor = [
        {
          author: {
            login: 'author-user',
            name: 'Author User',
            avatarUrl: 'https://example.com/author-avatar.jpg',
          },
          body: 'Milestone with author',
          closedIssuesCount: 3,
          createdAt: new Date(Date.now() - 10000000).toISOString(),
          openIssuesCount: 1,
          repositoryName: 'test-repo',
          organizationName: 'test-org',
          state: 'open',
          title: 'Milestone With Author',
          url: 'https://github.com/test/project/milestone/1',
        },
      ]

      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: milestonesWithAuthor,
        showAvatar: true,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText('Milestone With Author')).toBeInTheDocument()
      // The avatar image should be rendered
      const avatarImg = screen.getByAltText("Author User's avatar")
      expect(avatarImg).toBeInTheDocument()
      expect(avatarImg).toHaveAttribute('src', 'https://example.com/author-avatar.jpg')
    })

    it('renders milestone without author avatar when author data is missing', () => {
      const milestonesWithoutAuthor = [
        {
          author: null,
          body: 'Milestone without author',
          closedIssuesCount: 3,
          createdAt: new Date(Date.now() - 10000000).toISOString(),
          openIssuesCount: 1,
          repositoryName: 'test-repo',
          organizationName: 'test-org',
          state: 'open',
          title: 'Milestone No Author',
          url: 'https://github.com/test/project/milestone/1',
        },
      ]

      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: milestonesWithoutAuthor,
        showAvatar: true,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText('Milestone No Author')).toBeInTheDocument()
    })

    it('renders milestone title without link when URL is missing', () => {
      const milestonesWithoutUrl = [
        {
          author: mockUser,
          body: 'Milestone without URL',
          closedIssuesCount: 3,
          createdAt: new Date(Date.now() - 10000000).toISOString(),
          openIssuesCount: 1,
          repositoryName: 'test-repo',
          organizationName: 'test-org',
          state: 'open',
          title: 'Milestone No URL',
          url: null,
        },
      ]

      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: milestonesWithoutUrl,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText('Milestone No URL')).toBeInTheDocument()
      // The title should not be a link
      const title = screen.getByText('Milestone No URL')
      expect(title.closest('a')).toBeNull()
    })

    it('renders milestone without repository link when repositoryName or organizationName is missing', () => {
      const milestonesWithoutRepo = [
        {
          author: mockUser,
          body: 'Milestone without repo',
          closedIssuesCount: 3,
          createdAt: new Date(Date.now() - 10000000).toISOString(),
          openIssuesCount: 1,
          repositoryName: null,
          organizationName: null,
          state: 'open',
          title: 'Milestone No Repo',
          url: 'https://github.com/test/project/milestone/1',
        },
      ]

      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        recentMilestones: milestonesWithoutRepo,
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText('Milestone No Repo')).toBeInTheDocument()
    })
  })

  describe('Module Pull Requests Display', () => {
    const createPullRequests = (count: number) => {
      const pullRequests = []
      for (let i = 0; i < count; i++) {
        pullRequests.push({
          id: `pr-${i}`,
          author: mockUser,
          createdAt: new Date().toISOString(),
          organizationName: 'test-org',
          title: `Pull Request ${i + 1}`,
          url: `https://github.com/test/project/pull/${i + 1}`,
          state: 'OPEN',
          number: i + 1,
          mergedAt: null,
          repositoryName: 'test-repo',
        })
      }
      return pullRequests
    }

    it('renders only first 4 PRs initially for module type', () => {
      const manyPRs = createPullRequests(6)
      const moduleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'module' as const,
        pullRequests: manyPRs as unknown as PullRequest[],
      }

      render(<CardDetailsPage {...moduleProps} />)

      expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()

      expect(screen.getByText(/Pull Request 1/)).toBeInTheDocument()
      expect(screen.getByText(/Pull Request 4/)).toBeInTheDocument()

      expect(screen.queryByText(/Pull Request 5/)).not.toBeInTheDocument()
      expect(screen.queryByText(/Pull Request 6/)).not.toBeInTheDocument()

      expect(screen.getByText(/Show more/i)).toBeInTheDocument()
    })

    it('expands to show all PRs when "Show more" is clicked', () => {
      const manyPRs = createPullRequests(6)
      const moduleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'module' as const,
        pullRequests: manyPRs as unknown as PullRequest[],
      }

      render(<CardDetailsPage {...moduleProps} />)

      const showMoreBtn = screen.getByText(/Show more/i)
      fireEvent.click(showMoreBtn)

      expect(screen.getByText(/Pull Request 5/)).toBeInTheDocument()
      expect(screen.getByText(/Pull Request 6/)).toBeInTheDocument()

      expect(screen.getByText(/Show less/i)).toBeInTheDocument()
    })

    it('collapses back to 4 PRs when "Show less" is clicked', () => {
      const manyPRs = createPullRequests(6)
      const moduleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'module' as const,
        pullRequests: manyPRs as unknown as PullRequest[],
      }

      render(<CardDetailsPage {...moduleProps} />)

      fireEvent.click(screen.getByText(/Show more/i))
      expect(screen.getByText(/Pull Request 5/)).toBeInTheDocument()

      fireEvent.click(screen.getByText(/Show less/i))

      expect(screen.queryByText(/Pull Request 5/)).not.toBeInTheDocument()
      expect(screen.getByText(/Show more/i)).toBeInTheDocument()
    })

    it('does not show toggle button if PRs <= 4', () => {
      const fewPRs = createPullRequests(4)
      const moduleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'module' as const,
        pullRequests: fewPRs as unknown as PullRequest[],
      }

      render(<CardDetailsPage {...moduleProps} />)

      expect(screen.getByText(/Pull Request 1/)).toBeInTheDocument()
      expect(screen.getByText(/Pull Request 4/)).toBeInTheDocument()
      expect(screen.queryByText(/Show more/i)).not.toBeInTheDocument()
    })
  })

  describe('Module Admin EntityActions and Mentees', () => {
    it('renders EntityActions for module type when user is an admin', () => {
      const { useSession } = jest.requireMock('next-auth/react')
      useSession.mockReturnValue({
        data: {
          user: {
            login: 'admin-user',
            name: 'Admin User',
            email: 'admin@example.com',
          },
        },
      })

      const adminUser = {
        id: 'admin-id',
        login: 'admin-user',
        name: 'Admin User',
        avatarUrl: 'https://example.com/admin-avatar.jpg',
      }

      const moduleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'module' as const,
        accessLevel: 'admin',
        admins: [adminUser],
        programKey: 'test-program',
        entityKey: 'test-module',
        modules: [],
      }

      render(<CardDetailsPage {...moduleProps} />)

      expect(screen.getByTestId('entity-actions')).toBeInTheDocument()
      expect(screen.getByTestId('entity-actions')).toHaveTextContent('type=module')
    })

    it('does not render EntityActions for module type when user is not an admin', () => {
      const { useSession } = jest.requireMock('next-auth/react')
      useSession.mockReturnValue({
        data: {
          user: {
            login: 'regular-user',
            name: 'Regular User',
            email: 'user@example.com',
          },
        },
      })

      const adminUser = {
        id: 'admin-id',
        login: 'admin-user',
        name: 'Admin User',
        avatarUrl: 'https://example.com/admin-avatar.jpg',
      }

      const moduleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'module' as const,
        accessLevel: 'admin',
        admins: [adminUser],
        programKey: 'test-program',
        entityKey: 'test-module',
        modules: [],
      }

      render(<CardDetailsPage {...moduleProps} />)

      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('renders mentees section when mentees are provided', () => {
      const mentees = [
        {
          id: 'mentee-1',
          login: 'mentee_user1',
          name: 'Mentee User 1',
          avatarUrl: 'https://example.com/mentee1.jpg',
        },
        {
          id: 'mentee-2',
          login: 'mentee_user2',
          name: 'Mentee User 2',
          avatarUrl: 'https://example.com/mentee2.jpg',
        },
      ]

      const propsWithMentees: DetailsCardProps = {
        ...defaultProps,
        mentees,
        programKey: 'test-program',
        entityKey: 'test-entity',
      }

      render(<CardDetailsPage {...propsWithMentees} />)

      const allContributorsLists = screen.getAllByTestId('contributors-list')
      const menteesSection = allContributorsLists.find((el) => el.textContent?.includes('Mentees'))
      expect(menteesSection).toHaveTextContent('Mentees (2 items, max display: 6)')
    })

    it('does not render mentees section when no mentees are provided', () => {
      const propsWithoutMentees: DetailsCardProps = {
        ...defaultProps,
        mentees: [],
      }
      render(<CardDetailsPage {...propsWithoutMentees} />)
      // Make sure mentees section is not rendered
      const allContributorsLists = screen.queryAllByTestId('contributors-list')
      const menteesList = allContributorsLists.find((el) => el.textContent?.includes('Mentees'))
      expect(menteesList).toBeUndefined()
    })

    it('renders mentees with custom URL formatter', () => {
      const mentees = [
        {
          id: 'mentee-1',
          login: 'test_mentee',
          name: 'Test Mentee',
          avatarUrl: 'https://example.com/mentee.jpg',
        },
      ]

      const propsWithMentees: DetailsCardProps = {
        ...defaultProps,
        mentees,
        programKey: 'program-key-123',
        entityKey: 'entity-key-456',
      }

      render(<CardDetailsPage {...propsWithMentees} />)

      const allContributorsLists = screen.getAllByTestId('contributors-list')
      const menteesSection = allContributorsLists.find((el) => el.textContent?.includes('Mentees'))
      expect(menteesSection).toHaveTextContent('Mentees (1 items, max display: 6)')
    })

    it('handles null/undefined mentees array gracefully', () => {
      const propsWithNullMentees: DetailsCardProps = {
        ...defaultProps,
        mentees: null,
      }

      expect(() => render(<CardDetailsPage {...propsWithNullMentees} />)).not.toThrow()
    })

    it('renders program EntityActions when type is program with appropriate access', () => {
      const { useSession } = jest.requireMock('next-auth/react')
      useSession.mockReturnValue({
        data: {
          user: {
            login: 'program-admin',
            name: 'Program Admin',
            email: 'admin@example.com',
          },
        },
      })

      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        accessLevel: 'admin',
        canUpdateStatus: true,
        status: 'active',
        setStatus: jest.fn(),
        programKey: 'test-program',
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByTestId('entity-actions')).toBeInTheDocument()
      expect(screen.getByTestId('entity-actions')).toHaveTextContent('type=program')
    })

    it('does not render program EntityActions when canUpdateStatus is false', () => {
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        accessLevel: 'admin',
        canUpdateStatus: false,
        status: 'active',
        setStatus: jest.fn(),
        programKey: 'test-program',
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('does not render program EntityActions when accessLevel is not admin', () => {
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        accessLevel: 'user',
        canUpdateStatus: true,
        status: 'active',
        setStatus: jest.fn(),
        programKey: 'test-program',
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })
  })

  describe('Program and Module Tags, Domains, and Labels', () => {
    it('renders tags for program type', () => {
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        tags: ['tag1', 'tag2', 'tag3'],
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText(/Tags/)).toBeInTheDocument()
      expect(screen.getByText(/tag1, tag2, tag3/)).toBeInTheDocument()
    })

    it('renders domains for program type', () => {
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        domains: ['domain1', 'domain2'],
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText(/Domains/)).toBeInTheDocument()
      expect(screen.getByText(/domain1, domain2/)).toBeInTheDocument()
    })

    it('renders labels for program type', () => {
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        labels: ['label1', 'label2'],
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText(/Labels/)).toBeInTheDocument()
      expect(screen.getByText(/label1, label2/)).toBeInTheDocument()
    })

    it('renders tags and domains in same row for module type', () => {
      const moduleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'module' as const,
        tags: ['moduleTag1'],
        domains: ['moduleDomain1'],
        modules: [],
      }

      render(<CardDetailsPage {...moduleProps} />)

      expect(screen.getByText(/Tags/)).toBeInTheDocument()
      expect(screen.getByText(/Domains/)).toBeInTheDocument()
    })

    it('does not render tags section when tags array is empty', () => {
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        tags: [],
        domains: ['domain1'],
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.queryByText(/Tags:/)).not.toBeInTheDocument()
      expect(screen.getByText(/Domains/)).toBeInTheDocument()
    })

    it('does not render domains section when domains array is empty', () => {
      const programProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        tags: ['tag1'],
        domains: [],
        modules: [],
      }

      render(<CardDetailsPage {...programProps} />)

      expect(screen.getByText(/Tags/)).toBeInTheDocument()
      expect(screen.queryByText(/Domains:/)).not.toBeInTheDocument()
    })
  })

  describe('Program Module Rendering', () => {
    const mockModules = [
      {
        id: 'module-1-id',
        key: 'module-1',
        name: 'Module 1',
        description: 'First module',
        endedAt: new Date(Date.now() + 86400000).toISOString(),
        startedAt: new Date(Date.now() - 86400000).toISOString(),
        experienceLevel: 'BEGINNER',
        mentors: [],
      },
      {
        id: 'module-2-id',
        key: 'module-2',
        name: 'Module 2',
        description: 'Second module',
        endedAt: new Date(Date.now() + 86400000).toISOString(),
        startedAt: new Date(Date.now() - 86400000).toISOString(),
        experienceLevel: 'INTERMEDIATE',
        mentors: [],
      },
    ] as DetailsCardProps['modules']

    it('renders single module without SecondaryCard wrapper', () => {
      const singleModuleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        modules: [mockModules![0]],
      }

      render(<CardDetailsPage {...singleModuleProps} />)

      expect(screen.getByTestId('module-card')).toBeInTheDocument()
      // Single module should not have "Modules" title
      expect(screen.queryByText('Modules')).not.toBeInTheDocument()
    })

    it('renders multiple modules with SecondaryCard wrapper and title', () => {
      const multiModuleProps: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        modules: mockModules,
      }

      render(<CardDetailsPage {...multiModuleProps} />)

      expect(screen.getByTestId('module-card')).toBeInTheDocument()
      expect(screen.getByText('Modules')).toBeInTheDocument()
    })
  })

  describe('Mentors and Admins Lists', () => {
    const mockMentors = [
      {
        id: 'mentor-1',
        login: 'mentor_user1',
        name: 'Mentor User 1',
        avatarUrl: 'https://example.com/mentor1.jpg',
      },
      {
        id: 'mentor-2',
        login: 'mentor_user2',
        name: 'Mentor User 2',
        avatarUrl: 'https://example.com/mentor2.jpg',
      },
    ]

    const mockAdmins = [
      {
        id: 'admin-1',
        login: 'admin_user1',
        name: 'Admin User 1',
        avatarUrl: 'https://example.com/admin1.jpg',
      },
    ]

    it('renders mentors section when mentors are provided', () => {
      const propsWithMentors: DetailsCardProps = {
        ...defaultProps,
        mentors: mockMentors,
      }

      render(<CardDetailsPage {...propsWithMentors} />)

      const allContributorsLists = screen.getAllByTestId('contributors-list')
      const mentorsSection = allContributorsLists.find((el) => el.textContent?.includes('Mentors'))
      expect(mentorsSection).toHaveTextContent('Mentors (2 items, max display: 6)')
    })

    it('does not render mentors section when mentors array is empty', () => {
      const propsWithoutMentors: DetailsCardProps = {
        ...defaultProps,
        mentors: [],
      }

      render(<CardDetailsPage {...propsWithoutMentors} />)

      // Mentors section should not be rendered
      const allContributorsLists = screen.queryAllByTestId('contributors-list')
      const mentorsSection = allContributorsLists.find((el) => el.textContent?.includes('Mentors'))
      expect(mentorsSection).toBeUndefined()
    })

    it('renders admins section when type is program and admins are provided', () => {
      const propsWithAdmins: DetailsCardProps = {
        ...defaultProps,
        type: 'program' as const,
        admins: mockAdmins,
        modules: [],
      }

      render(<CardDetailsPage {...propsWithAdmins} />)

      const allContributorsLists = screen.getAllByTestId('contributors-list')
      const adminsSection = allContributorsLists.find((el) => el.textContent?.includes('Admins'))
      expect(adminsSection).toHaveTextContent('Admins (1 items, max display: 6)')
    })

    it('does not render admins section for non-program types', () => {
      const propsWithAdmins: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        admins: mockAdmins,
      }

      render(<CardDetailsPage {...propsWithAdmins} />)

      const allContributorsLists = screen.queryAllByTestId('contributors-list')
      const adminsSection = allContributorsLists.find((el) => el.textContent?.includes('Admins'))
      expect(adminsSection).toBeUndefined()
    })
  })

  describe('Repository Rendering for Different Types', () => {
    it('renders repositories for user type', () => {
      const userProps: DetailsCardProps = {
        ...defaultProps,
        type: 'user' as const,
        repositories: mockRepositories,
      }

      render(<CardDetailsPage {...userProps} />)

      expect(screen.getByText('Repositories')).toBeInTheDocument()
      expect(screen.getByTestId('repositories-card')).toBeInTheDocument()
    })

    it('renders repositories for organization type', () => {
      const orgProps: DetailsCardProps = {
        ...defaultProps,
        type: 'organization' as const,
        repositories: mockRepositories,
      }

      render(<CardDetailsPage {...orgProps} />)

      expect(screen.getByText('Repositories')).toBeInTheDocument()
      expect(screen.getByTestId('repositories-card')).toBeInTheDocument()
    })

    it('does not render repositories for chapter type', () => {
      const chapterProps: DetailsCardProps = {
        ...defaultProps,
        type: 'chapter' as const,
        repositories: mockRepositories,
      }

      render(<CardDetailsPage {...chapterProps} />)

      expect(screen.queryByText('Repositories')).not.toBeInTheDocument()
    })
  })

  describe('Sponsor Card Rendering', () => {
    it('renders sponsor card for chapter type', () => {
      const chapterProps: DetailsCardProps = {
        ...defaultProps,
        type: 'chapter' as const,
        entityKey: 'test-chapter',
      }

      render(<CardDetailsPage {...chapterProps} />)

      expect(screen.getByTestId('sponsor-card')).toBeInTheDocument()
      expect(screen.getByTestId('sponsor-card')).toHaveTextContent('Type: chapter')
    })

    it('renders sponsor card for repository type', () => {
      const repoProps: DetailsCardProps = {
        ...defaultProps,
        type: 'repository' as const,
        entityKey: 'test-repo',
      }

      render(<CardDetailsPage {...repoProps} />)

      expect(screen.getByTestId('sponsor-card')).toBeInTheDocument()
      expect(screen.getByTestId('sponsor-card')).toHaveTextContent('Type: project')
    })

    it('uses projectName as title when provided', () => {
      const projectProps: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        entityKey: 'test-project',
        projectName: 'Custom Project Name',
      }

      render(<CardDetailsPage {...projectProps} />)

      expect(screen.getByTestId('sponsor-card')).toHaveTextContent('Title: Custom Project Name')
    })

    it('does not render sponsor card when entityKey is missing', () => {
      const propsWithoutKey: DetailsCardProps = {
        ...defaultProps,
        type: 'project' as const,
        entityKey: undefined,
      }

      render(<CardDetailsPage {...propsWithoutKey} />)

      expect(screen.queryByTestId('sponsor-card')).not.toBeInTheDocument()
    })
  })
})
