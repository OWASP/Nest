import { useQuery } from '@apollo/client/react'
import { mockProjectsDashboardMetricsDetailsData } from '@mockData/mockProjectsDashboardMetricsDetailsData'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import ProjectHealthMetricsDetails from 'app/projects/dashboard/metrics/[projectKey]/page'

jest.mock('react-apexcharts', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-apexcharts">Mock ApexChart</div>
    },
  }
})

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div title={content}>
      {children}
      <span style={{ display: 'none' }}>{content}</span>
    </div>
  ),
}))
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))
jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    projectKey: 'test-project',
  })),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: () => ({
    isSyncing: false,
  }),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('ProjectHealthMetricsDetails', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectsDashboardMetricsDetailsData,
      loading: false,
      error: null,
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
    render(<ProjectHealthMetricsDetails />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders error state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: mockError,
    })
    render(<ProjectHealthMetricsDetails />)
    const errorMessage = screen.getByText('No metrics data available for this project.')
    await waitFor(() => {
      expect(errorMessage).toBeInTheDocument()
    })
  })

  test('renders project health metrics details', async () => {
    const headers = [
      'Days Metrics',
      'Issues',
      'Stars',
      'Forks',
      'Contributors',
      'Releases',
      'Open Pull Requests',
      'Health',
      'Score',
    ]
    const metrics = mockProjectsDashboardMetricsDetailsData.project.healthMetricsLatest
    render(<ProjectHealthMetricsDetails />)
    await waitFor(() => {
      for (const header of headers) {
        expect(screen.getByText(header)).toBeInTheDocument()
      }
      expect(screen.getByText(metrics.projectName)).toBeInTheDocument()
      expect(screen.getByText(metrics.score.toString())).toBeInTheDocument()
    })
  })

  test('renders non-compliant status when funding requirements are not met', async () => {
    const nonCompliantData = {
      ...mockProjectsDashboardMetricsDetailsData,
      project: {
        ...mockProjectsDashboardMetricsDetailsData.project,
        healthMetricsLatest: {
          ...mockProjectsDashboardMetricsDetailsData.project.healthMetricsLatest,
          isFundingRequirementsCompliant: false,
          isLeaderRequirementsCompliant: true,
        },
      },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: nonCompliantData,
      loading: false,
      error: null,
    })

    render(<ProjectHealthMetricsDetails />)

    await waitFor(() => {
      expect(screen.getByText('Funding Requirements Not Compliant')).toBeInTheDocument()
      expect(screen.getByText('Leader Requirements Compliant')).toBeInTheDocument()
    })
  })

  test('renders non-compliant status when leader requirements are not met', async () => {
    const nonCompliantData = {
      ...mockProjectsDashboardMetricsDetailsData,
      project: {
        ...mockProjectsDashboardMetricsDetailsData.project,
        healthMetricsLatest: {
          ...mockProjectsDashboardMetricsDetailsData.project.healthMetricsLatest,
          isFundingRequirementsCompliant: true,
          isLeaderRequirementsCompliant: false,
        },
      },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: nonCompliantData,
      loading: false,
      error: null,
    })

    render(<ProjectHealthMetricsDetails />)

    await waitFor(() => {
      expect(screen.getByText('Funding Requirements Compliant')).toBeInTheDocument()
      expect(screen.getByText('Leader Requirements Not Compliant')).toBeInTheDocument()
    })
  })

  test('handles null createdAt in metrics list gracefully', async () => {
    const dataWithNullCreatedAt = {
      ...mockProjectsDashboardMetricsDetailsData,
      project: {
        ...mockProjectsDashboardMetricsDetailsData.project,
        healthMetricsList: [
          {
            ...mockProjectsDashboardMetricsDetailsData.project.healthMetricsList[0],
            createdAt: null,
          },
        ],
      },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: dataWithNullCreatedAt,
      loading: false,
      error: null,
    })

    render(<ProjectHealthMetricsDetails />)

    await waitFor(() => {
      expect(screen.getByText('Stars')).toBeInTheDocument()
    })
  })

  test('handles null score and compliance flags gracefully', async () => {
    const dataWithNullValues = {
      ...mockProjectsDashboardMetricsDetailsData,
      project: {
        ...mockProjectsDashboardMetricsDetailsData.project,
        healthMetricsLatest: {
          ...mockProjectsDashboardMetricsDetailsData.project.healthMetricsLatest,
          score: null,
          isFundingRequirementsCompliant: null,
          isLeaderRequirementsCompliant: null,
        },
      },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: dataWithNullValues,
      loading: false,
      error: null,
    })

    render(<ProjectHealthMetricsDetails />)

    await waitFor(() => {
      expect(screen.getByText('Funding Requirements Not Compliant')).toBeInTheDocument()
      expect(screen.getByText('Leader Requirements Not Compliant')).toBeInTheDocument()
    })
  })

  test('handles null metric counts gracefully', async () => {
    const dataWithNullCounts = {
      ...mockProjectsDashboardMetricsDetailsData,
      project: {
        ...mockProjectsDashboardMetricsDetailsData.project,
        healthMetricsList: [
          {
            ...mockProjectsDashboardMetricsDetailsData.project.healthMetricsList[0],
            starsCount: null,
            forksCount: null,
            openIssuesCount: null,
            unassignedIssuesCount: null,
            unansweredIssuesCount: null,
            totalIssuesCount: null,
            openPullRequestsCount: null,
            recentReleasesCount: null,
            totalReleasesCount: null,
            contributorsCount: null,
          },
        ],
        healthMetricsLatest: {
          ...mockProjectsDashboardMetricsDetailsData.project.healthMetricsLatest,
          ageDays: null,
          lastCommitDays: null,
          lastReleaseDays: null,
          lastPullRequestDays: null,
          owaspPageLastUpdateDays: null,
          ageDaysRequirement: null,
          lastCommitDaysRequirement: null,
          lastReleaseDaysRequirement: null,
          lastPullRequestDaysRequirement: null,
          owaspPageLastUpdateDaysRequirement: null,
        },
      },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: dataWithNullCounts,
      loading: false,
      error: null,
    })

    render(<ProjectHealthMetricsDetails />)

    await waitFor(() => {
      expect(screen.getByText('Days Metrics')).toBeInTheDocument()
      expect(screen.getByText('Stars')).toBeInTheDocument()
    })
  })
})
