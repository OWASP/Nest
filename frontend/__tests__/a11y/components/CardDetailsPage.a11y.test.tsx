import { mockChapterData } from '@mockData/mockChapterData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import React from 'react'
import { FaCode, FaTags } from 'react-icons/fa6'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { DetailsCardProps } from 'types/card'
import DetailsCard from 'components/CardDetailsPage'

jest.mock('next/link', () => {
  return function MockLink({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode
    href: string
    [key: string]: unknown
  }) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

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

jest.mock('react-apexcharts', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-chart" />,
}))

jest.mock('next/dynamic', () => ({
  __esModule: true,
  default: () => {
    return function MockDynamicComponent({
      children,
      ...props
    }: React.ComponentPropsWithoutRef<'div'>) {
      return <div {...props}>{children}</div>
    }
  },
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({ data: null, status: 'unauthenticated' })),
}))

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

describe('CardDetailsPage a11y', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<DetailsCard {...defaultProps} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations for chapter type', async () => {
    const { container } = render(
      <DetailsCard
        {...defaultProps}
        type="chapter"
        geolocationData={[{ ...mockChapterData.chapters[0], suggestedLocation: 'Sample location' }]}
      />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should have no violations for program type', async () => {
    const { container } = render(
      <DetailsCard
        {...defaultProps}
        type="program"
        accessLevel="admin"
        modules={[
          {
            id: 'module1',
            key: 'mod-001',
            name: 'Intro to Web',
            description: 'A beginner friendly module.',
            experienceLevel: ExperienceLevelEnum.Beginner,
            startedAt: 1735689600, // 2025-01-01
            endedAt: 1740787200, // 2025-03-01
            mentors: [
              {
                id: 'mentor-mentor1',
                login: 'mentor1',
                avatarUrl: 'https://avatars.githubusercontent.com/u/12345',
                name: 'Mentor One',
              },
            ],
            tags: ['tag1'],
            domains: ['domain1'],
          },
        ]}
      />
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations in archived state', async () => {
    let container: HTMLElement

    await React.act(async () => {
      const renderResult = render(
        <DetailsCard {...defaultProps} isActive={false} isArchived={true} />
      )
      container = renderResult.container
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
