import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import DetailsCard from 'components/CardDetailsPage'
import { DetailsCardProps } from 'types/card'

// Mock the components that are used in CardDetailsPage
jest.mock('components/AnchorTitle', () => ({ title }: { title: string }) => (
  <div data-testid={`anchor-title-${title.toLowerCase()}`}>{title}</div>
))

jest.mock('components/ChapterMapWrapper', () => ({
  __esModule: true,
  default: ({ geoLocData }: { geoLocData: any; showLocal: boolean; style: any }) => (
    <div data-testid="chapter-map-wrapper">Map Component</div>
  ),
}))

jest.mock('components/HealthMetrics', () => ({
  __esModule: true,
  default: ({ data }: { data: any[] }) => (
    <div data-testid="health-metrics">Health Metrics Component</div>
  ),
}))

jest.mock('components/InfoBlock', () => ({
  __esModule: true,
  default: ({ icon, pluralizedName, unit, value }: any) => (
    <div data-testid={`info-block-${pluralizedName || 'unknown'}`}>
      {value} {pluralizedName} {unit}
    </div>
  ),
}))

jest.mock('components/LeadersList', () => ({
  __esModule: true,
  default: ({ leaders }: { leaders: string }) => (
    <div data-testid="leaders-list">{leaders}</div>
  ),
}))

jest.mock('components/MetricsScoreCircle', () => ({
  __esModule: true,
  default: ({ score }: { score: number }) => (
    <div data-testid="metrics-score-circle">Score: {score}</div>
  ),
}))

jest.mock('components/Milestones', () => ({
  __esModule: true,
  default: ({ data, showAvatar }: { data: any[]; showAvatar: boolean }) => (
    <div data-testid="milestones-component">Milestones Component</div>
  ),
}))

jest.mock('components/RecentIssues', () => ({
  __esModule: true,
  default: ({ data, showAvatar }: { data: any[]; showAvatar: boolean }) => (
    <div data-testid="recent-issues-component">Recent Issues Component</div>
  ),
}))

jest.mock('components/RecentPullRequests', () => ({
  __esModule: true,
  default: ({ data, showAvatar }: { data: any[]; showAvatar: boolean }) => (
    <div data-testid="recent-pull-requests-component">Recent Pull Requests Component</div>
  ),
}))

jest.mock('components/RecentReleases', () => ({
  __esModule: true,
  default: ({
    data,
    showAvatar,
    showSingleColumn,
  }: {
    data: any[]
    showAvatar: boolean
    showSingleColumn: boolean
  }) => <div data-testid="recent-releases-component">Recent Releases Component</div>,
}))

jest.mock('components/RepositoriesCard', () => ({
  __esModule: true,
  default: ({ repositories }: { repositories: any[] }) => (
    <div data-testid="repositories-card-component">Repositories Card Component</div>
  ),
}))

jest.mock('components/SecondaryCard', () => {
  return {
    __esModule: true,
    default: ({
      icon,
      title,
      children,
      className,
    }: {
      icon: any
      title: React.ReactNode
      children: React.ReactNode
      className?: string
    }) => (
      <div data-testid={`secondary-card-${title?.toString().toLowerCase() || 'unknown'}`} className={className}>
        {title}
        <div>{children}</div>
      </div>
    ),
  }
})

jest.mock('components/SponsorCard', () => ({
  __esModule: true,
  default: ({
    target,
    title,
    type,
  }: {
    target: string
    title: string
    type: string
  }) => <div data-testid="sponsor-card-component">Sponsor Card for {title}</div>,
}))

jest.mock('components/ToggleableList', () => ({
  __esModule: true,
  default: ({
    items,
    icon,
    label,
  }: {
    items: string[]
    icon: any
    label: React.ReactNode
  }) => (
    <div data-testid={`toggleable-list-${label?.toString().toLowerCase() || 'unknown'}`}>
      {label}
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  ),
}))

jest.mock('components/TopContributorsList', () => ({
  __esModule: true,
  default: ({
    contributors,
    icon,
    maxInitialDisplay,
  }: {
    contributors: any[]
    icon: any
    maxInitialDisplay: number
  }) => <div data-testid="top-contributors-list">Top Contributors List</div>,
}))

jest.mock('next/link', () => {
  return ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href} data-testid="next-link">
      {children}
    </a>
  )
})

// Mock the utils
jest.mock('utils/credentials', () => ({
  IS_PROJECT_HEALTH_ENABLED: true,
}))

jest.mock('utils/capitalize', () => ({
  capitalize: (str: string) => str.charAt(0).toUpperCase() + str.slice(1),
}))

jest.mock('utils/urlIconMappings', () => ({
  getSocialIcon: (url: string) => 'mockIcon',
}))
// Add mock for FontAwesomeIcon to support accessibility testing
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon }: { icon: any }) => <svg role="img" aria-hidden="true" />,
}))

// Minimal required props for the component
const minimalProps: DetailsCardProps = {
  title: 'Test Project',
  description: 'Test description',
  type: 'project',
  stats: [],
}

describe('DetailsCard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders successfully with minimal required props', () => {
    render(<DetailsCard {...minimalProps} />)
    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('Test description')).toBeInTheDocument()
  })

  it('renders inactive status when isActive is false', () => {
    render(<DetailsCard {...minimalProps} isActive={false} />)
    expect(screen.getByText('Inactive')).toBeInTheDocument()
  })

  it('does not render inactive status when isActive is true', () => {
    render(<DetailsCard {...minimalProps} isActive={true} />)
    expect(screen.queryByText('Inactive')).not.toBeInTheDocument()
  })

  it('renders summary when provided', () => {
    const props = {
      ...minimalProps,
      summary: 'This is a summary of the project',
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('secondary-card-summary')).toBeInTheDocument()
    expect(screen.getByText('This is a summary of the project')).toBeInTheDocument()
  })

  it('renders userSummary when provided', () => {
    const userSummaryElement = <div>Custom User Summary</div>
    const props = {
      ...minimalProps,
      userSummary: userSummaryElement,
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('secondary-card-summary')).toBeInTheDocument()
  })

  it('renders heatmap when provided', () => {
    const heatmapElement = <div>Heatmap Content</div>
    const props = {
      ...minimalProps,
      heatmap: heatmapElement,
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('secondary-card-contribution heatmap')).toBeInTheDocument()
  })

  it('renders details with correct title based on type', () => {
    const props = {
      ...minimalProps,
      details: [
        { label: 'Created', value: '2023-01-01' },
        { label: 'Updated', value: '2023-02-01' },
      ],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('anchor-title-project details')).toBeInTheDocument()
    expect(screen.getByText('Created:')).toBeInTheDocument()
    expect(screen.getByText('Updated:')).toBeInTheDocument()
  })

  it('renders leaders list correctly when details include Leaders', () => {
    const props = {
      ...minimalProps,
      details: [
        { label: 'Leaders', value: 'John Doe, Jane Smith' },
      ],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('leaders-list')).toBeInTheDocument()
    expect(screen.getByText('Leaders:')).toBeInTheDocument()
  })

  it('renders statistics when provided for project type', () => {
    const props = {
      ...minimalProps,
      stats: [
        { icon: null, pluralizedName: 'Stars', value: 100 },
        { icon: null, pluralizedName: 'Forks', value: 50 },
      ],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('secondary-card-statistics')).toBeInTheDocument()
    expect(screen.getByTestId('info-block-stars')).toBeInTheDocument()
    expect(screen.getByTestId('info-block-forks')).toBeInTheDocument()
  })

  it('renders chapter map for chapter type with geolocation data', () => {
    const props = {
      ...minimalProps,
      type: 'chapter',
      geolocationData: [{ id: 1, name: 'Test Chapter' }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('chapter-map-wrapper')).toBeInTheDocument()
  })

  it('renders languages and topics for project type', () => {
    const props = {
      ...minimalProps,
      languages: ['JavaScript', 'TypeScript'],
      topics: ['Security', 'Web'],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('toggleable-list-languages')).toBeInTheDocument()
    expect(screen.getByTestId('toggleable-list-topics')).toBeInTheDocument()
    expect(screen.getByText('JavaScript')).toBeInTheDocument()
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
    expect(screen.getByText('Security')).toBeInTheDocument()
    expect(screen.getByText('Web')).toBeInTheDocument()
  })

  it('does not render languages section when languages array is empty', () => {
    const props = {
      ...minimalProps,
      languages: [],
      topics: ['Security', 'Web'],
    }
    render(<DetailsCard {...props} />)
    expect(screen.queryByTestId('toggleable-list-languages')).not.toBeInTheDocument()
    expect(screen.getByTestId('toggleable-list-topics')).toBeInTheDocument()
  })

  it('does not render topics section when topics array is empty', () => {
    const props = {
      ...minimalProps,
      languages: ['JavaScript', 'TypeScript'],
      topics: [],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('toggleable-list-languages')).toBeInTheDocument()
    expect(screen.queryByTestId('toggleable-list-topics')).not.toBeInTheDocument()
  })

  it('renders top contributors when provided', () => {
    const props = {
      ...minimalProps,
      topContributors: [{ id: 1, name: 'Contributor 1' }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('top-contributors-list')).toBeInTheDocument()
  })

  it('renders recent issues and milestones for project type', () => {
    const props = {
      ...minimalProps,
      recentIssues: [{ id: 1, title: 'Issue 1' }],
      recentMilestones: [{ id: 1, title: 'Milestone 1' }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('recent-issues-component')).toBeInTheDocument()
    expect(screen.getByTestId('milestones-component')).toBeInTheDocument()
  })

  it('renders pull requests and releases for project type', () => {
    const props = {
      ...minimalProps,
      pullRequests: [{ id: 1, title: 'PR 1' }],
      recentReleases: [{ id: 1, title: 'Release 1' }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('recent-pull-requests-component')).toBeInTheDocument()
    expect(screen.getByTestId('recent-releases-component')).toBeInTheDocument()
  })

  it('renders repositories for project type when repositories are provided', () => {
    const props = {
      ...minimalProps,
      repositories: [{ id: 1, name: 'Repo 1' }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('secondary-card-repositories')).toBeInTheDocument()
    expect(screen.getByTestId('repositories-card-component')).toBeInTheDocument()
  })

  it('renders health metrics for project type when health metrics data is provided', () => {
    const props = {
      ...minimalProps,
      healthMetricsData: [{ id: 1, score: 85 }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('health-metrics')).toBeInTheDocument()
  })

  it('renders metrics score circle when health metrics data is provided for project type', () => {
    const props = {
      ...minimalProps,
      healthMetricsData: [{ id: 1, score: 85 }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('metrics-score-circle')).toBeInTheDocument()
    expect(screen.getByText('Score: 85')).toBeInTheDocument()
  })

  it('renders sponsor card for project type when entityKey is provided', () => {
    const props = {
      ...minimalProps,
      entityKey: 'test-project',
      projectName: 'Test Project',
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByTestId('sponsor-card-component')).toBeInTheDocument()
  })

  it('renders social links for chapter type when socialLinks are provided', () => {
    const props = {
      ...minimalProps,
      type: 'chapter',
      socialLinks: ['https://twitter.com/test', 'https://github.com/test'],
      details: [{ label: 'Created', value: '2023-01-01' }],
    }
    render(<DetailsCard {...props} />)
    expect(screen.getByText('Social Links')).toBeInTheDocument()
    // Two social links should be rendered
    const socialIcons = screen.getAllByRole('link')
    expect(socialIcons).toHaveLength(2)
  })

  it('handles missing or undefined props gracefully', () => {
    // Minimal props with some undefined values
    const props = {
      ...minimalProps,
      description: undefined,
      details: undefined,
      stats: undefined,
    }
    
    // This should not throw an error
    expect(() => render(<DetailsCard {...props} />)).not.toThrow()
  })

  it('has the correct CSS classes for light/dark mode compatibility', () => {
    render(<DetailsCard {...minimalProps} />)
    
    // Check main container has appropriate classes
    const container = screen.getByText('Test Project').closest('div')
    expect(container).toHaveClass('dark:bg-[#212529]')
    expect(container).toHaveClass('dark:text-gray-300')
  })

  it('handles clicking on the metrics score circle link', () => {
    const props = {
      ...minimalProps,
      healthMetricsData: [{ id: 1, score: 85 }],
    }
    render(<DetailsCard {...props} />)
    
    const link = screen.getByTestId('next-link')
    expect(link).toHaveAttribute('href', '#issues-trend')
    
    // Simulate click on the link
    fireEvent.click(link)
  })

  it('handles clicking on social links', () => {
    const props = {
      ...minimalProps,
      type: 'chapter',
      socialLinks: ['https://twitter.com/test'],
      details: [{ label: 'Created', value: '2023-01-01' }],
    }
    render(<DetailsCard {...props} />)
    
    const socialLink = screen.getByRole('link')
    expect(socialLink).toHaveAttribute('href', 'https://twitter.com/test')
    expect(socialLink).toHaveAttribute('target', '_blank')
    expect(socialLink).toHaveAttribute('rel', 'noopener noreferrer')
    
    // Simulate click on the social link
    fireEvent.click(socialLink)
  })

  it('verifies accessibility attributes on links', () => {
    const props = {
      ...minimalProps,
      type: 'chapter',
      socialLinks: ['https://twitter.com/test'],
      details: [{ label: 'Created', value: '2023-01-01' }],
    }
    render(<DetailsCard {...props} />)
    
    // Check for proper accessibility attributes
    const socialLink = screen.getByRole('link')
    expect(socialLink).toHaveAttribute('rel', 'noopener noreferrer')
    
    // Verify FontAwesome icon has proper accessibility
    const icon = screen.getByRole('img', { hidden: true })
    expect(icon).toBeInTheDocument()
  })

  it('has proper semantic HTML structure', () => {
    render(<DetailsCard {...minimalProps} />)
    
    // Check for proper heading hierarchy
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('Test Project')
    
    // Check for proper paragraph elements
    const paragraph = screen.getByText('Test description')
    expect(paragraph.tagName).toBe('P')
  })

  it('applies proper grid layout classes for responsive design', () => {
    const props = {
      ...minimalProps,
      details: [{ label: 'Created', value: '2023-01-01' }],
      stats: [{ icon: null, pluralizedName: 'Stars', value: 100 }],
    }
    render(<DetailsCard {...props} />)
    
    // Check for grid layout classes
    const gridContainer = screen.getByTestId('secondary-card-project details').closest('div')
    expect(gridContainer).toHaveClass('grid')
    expect(gridContainer).toHaveClass('grid-cols-1')
    expect(gridContainer).toHaveClass('gap-6')
    expect(gridContainer).toHaveClass('md:grid-cols-7')
  })

  it('handles invalid inputs gracefully', () => {
    // Test with invalid data types
    const props = {
      ...minimalProps,
      // @ts-ignore - intentionally passing wrong type for testing
      stats: 'not an array',
      // @ts-ignore - intentionally passing wrong type for testing
      details: 'not an array',
      // @ts-ignore - intentionally passing wrong type for testing
      languages: 'not an array',
    }
    
    // This should not throw an error
    expect(() => render(<DetailsCard {...props} />)).not.toThrow()
  })

  it('handles extremely long text content properly', () => {
    const longText = 'A'.repeat(1000)
    const props = {
      ...minimalProps,
      description: longText,
      summary: longText,
    }
    
    render(<DetailsCard {...props} />)
    
    // Component should render without breaking layout
    const container = screen.getByText('Test Project').closest('div')
    expect(container).toBeInTheDocument()
    
    // Long description should be contained in the document
    expect(screen.getByText(longText)).toBeInTheDocument()
  })
})