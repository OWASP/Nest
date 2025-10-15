import { faCode, faTags } from '@fortawesome/free-solid-svg-icons'
import { render, screen, cleanup } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import type { DetailsCardProps } from 'types/card'
import CardDetailsPage from 'components/CardDetailsPage'

jest.mock('next/link', () => {
  const MockLink = ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode
    href: string
    [key: string]: unknown
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  )
  MockLink.displayName = 'MockLink'
  return MockLink
})

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

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({
    icon,
    className,
    ...props
  }: {
    icon: { iconName: string }
    className?: string
    [key: string]: unknown
  }) => <span data-testid={`icon-${icon.iconName}`} className={className} {...props} />,
}))

jest.mock('utils/env.client', () => ({
  IS_PROJECT_HEALTH_ENABLED: true,
}))

jest.mock('utils/urlIconMappings', () => ({
  getSocialIcon: (url: string) => {
    if (url?.includes('github')) {
      return { iconName: 'github' }
    }
    if (url?.includes('twitter')) {
      return { iconName: 'twitter' }
    }
    return { iconName: 'link' }
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
    ...otherProps
  }: {
    geoLocData?: unknown
    showLocal: boolean
    style: React.CSSProperties
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

jest.mock('components/InfoBlock', () => ({
  __esModule: true,
  default: ({
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
  default: ({ leaders, ...props }: { leaders: string; [key: string]: unknown }) => (
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
  }) => (
    <div data-testid="metrics-score-circle" role={clickable ? 'button' : undefined} {...props}>
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

jest.mock('components/RepositoriesCard', () => ({
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
    ...props
  }: {
    _icon: unknown
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
    label,
    ...props
  }: {
    items: string[]
    _icon: unknown
    label: React.ReactNode
    [key: string]: unknown
  }) => (
    <div data-testid="toggleable-list" {...props}>
      {label}: {items.join(', ')}
    </div>
  ),
}))

jest.mock('components/TopContributorsList', () => ({
  __esModule: true,
  default: ({
    contributors,
    maxInitialDisplay,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    icon,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    label,
    ...props
  }: {
    contributors: unknown[]
    icon?: unknown
    label?: string
    maxInitialDisplay: number
    [key: string]: unknown
  }) => (
    <div data-testid="top-contributors-list" {...props}>
      Top Contributors ({contributors.length} items, max display: {maxInitialDisplay})
    </div>
  ),
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
      icon: faCode,
      pluralizedName: 'repositories',
      unit: '',
      value: 10,
    },
    {
      icon: faTags,
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
      avatarUrl: 'https://example.com/avatar1.jpg',
      login: 'john_doe',
      name: 'John Doe',
      projectKey: 'test-project',
      contributionsCount: 50,
    },
    {
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
      summary: 'Issue summary',
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
      author: mockUser,
      createdAt: new Date(Date.now() - 172800000).toISOString(),
      organizationName: 'test-org',
      title: 'Add new feature',
      url: 'https://github.com/test/project/pull/456',
    },
  ]

  const mockRecentReleases = [
    {
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
      // Updated classes for consistent badge styling
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

    const supportedTypes = ['project', 'repository', 'committee', 'user', 'organization']

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

    it('renders social links with correct hrefs and target attributes', () => {
      const socialLinks = ['https://github.com/test', 'https://twitter.com/test']
      render(<CardDetailsPage {...defaultProps} type="chapter" socialLinks={socialLinks} />)

      const links = screen.getAllByRole('link')
      links.forEach((link) => {
        expect(link).toHaveAttribute('target', '_blank')
        expect(link).toHaveAttribute('rel', 'noopener noreferrer')
      })
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

      expect(screen.getByTestId('top-contributors-list')).toHaveTextContent(
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

    const entityTypes = ['project', 'repository', 'user', 'organization', 'committee', 'chapter']

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

    const supportedTypes = ['project', 'repository', 'committee', 'user', 'organization']

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
      expect(screen.getByTestId('top-contributors-list')).toHaveTextContent(
        'Top Contributors (2 items'
      )
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

      externalLinks.forEach((link) => {
        expect(link).toHaveAttribute('target', '_blank')
        expect(link).toHaveAttribute('rel', 'noopener noreferrer')
      })
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

      expect(screen.getByTestId('top-contributors-list')).toHaveTextContent(
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
      render(<CardDetailsPage {...defaultProps} type="unsupported-type" />)

      expect(screen.getByText('Unsupported-type Details')).toBeInTheDocument()
    })

    it('handles extremely large contributor arrays', () => {
      const largeContributors = Array.from({ length: 1000 }, (_, i) => ({
        ...mockContributors[0],
        login: `user-${i}`,
        name: `User ${i}`,
      }))

      render(<CardDetailsPage {...defaultProps} topContributors={largeContributors} />)

      expect(screen.getByTestId('top-contributors-list')).toHaveTextContent(
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
        type: 'project',
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
      const { rerender } = render(<CardDetailsPage {...defaultProps} type="project" />)

      rerender(<CardDetailsPage {...defaultProps} type="chapter" />)
      expect(screen.getByText('Chapter Details')).toBeInTheDocument()

      rerender(<CardDetailsPage {...defaultProps} type="user" />)
      expect(screen.getByText('User Details')).toBeInTheDocument()

      rerender(<CardDetailsPage {...defaultProps} type="organization" />)
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
      const fullPropsAllSections = {
        ...defaultProps,
        type: 'project',
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
      expect(screen.getByTestId('top-contributors-list')).toBeInTheDocument()
      expect(screen.getByTestId('repositories-card')).toBeInTheDocument()
      expect(screen.getByTestId('sponsor-card')).toBeInTheDocument()
    })

    it('handles zero and negative values in stats', () => {
      const statsWithZeroValues = [
        { icon: faCode, value: 0, unit: 'Star' },
        { icon: faTags, value: invalidValues.negativeNumber, unit: 'Issue' },
        { icon: faCode, value: invalidValues.nullValue, unit: 'Fork' },
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
      const archivedProps = {
        ...defaultProps,
        type: 'repository',
        isArchived: true,
      }

      render(<CardDetailsPage {...archivedProps} />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
    })

    it('does not display archived badge for non-archived repository', () => {
      const activeProps = {
        ...defaultProps,
        type: 'repository',
        isArchived: false,
      }

      render(<CardDetailsPage {...activeProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('does not display archived badge when isArchived is undefined', () => {
      const undefinedProps = {
        ...defaultProps,
        type: 'repository',
      }

      render(<CardDetailsPage {...undefinedProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('does not display archived badge for non-repository types', () => {
      const projectProps = {
        ...defaultProps,
        type: 'project',
        isArchived: true,
      }

      render(<CardDetailsPage {...projectProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })

    it('displays archived badge alongside inactive badge', () => {
      const bothBadgesProps = {
        ...defaultProps,
        type: 'repository',
        isArchived: true,
        isActive: false,
      }

      render(<CardDetailsPage {...bothBadgesProps} />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
      expect(screen.getByText('Inactive')).toBeInTheDocument()
    })

    it('displays archived badge independently of active status', () => {
      const archivedAndActiveProps = {
        ...defaultProps,
        type: 'repository',
        isArchived: true,
        isActive: true,
      }

      render(<CardDetailsPage {...archivedAndActiveProps} />)

      expect(screen.getByText('Archived')).toBeInTheDocument()
      expect(screen.queryByText('Inactive')).not.toBeInTheDocument()
    })

    it('archived badge has correct positioning with flex container', () => {
      const archivedProps = {
        ...defaultProps,
        type: 'repository',
        isArchived: true,
      }

      const { container } = render(<CardDetailsPage {...archivedProps} />)

      // New structure: badges are in a flex container with items-center and gap-3
      const badgeContainer = container.querySelector('.flex.items-center.gap-3')
      expect(badgeContainer).toBeInTheDocument()
    })

    it('archived badge renders with medium size', () => {
      const archivedProps = {
        ...defaultProps,
        type: 'repository',
        isArchived: true,
      }

      render(<CardDetailsPage {...archivedProps} />)

      const badge = screen.getByText('Archived')
      expect(badge).toHaveClass('px-3', 'py-1', 'text-sm')
    })

    it('handles null isArchived gracefully', () => {
      const nullArchivedProps = {
        ...defaultProps,
        type: 'repository',
        isArchived: null,
      }

      render(<CardDetailsPage {...nullArchivedProps} />)

      expect(screen.queryByText('Archived')).not.toBeInTheDocument()
    })
  })
})
