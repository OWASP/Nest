import { useQuery } from '@apollo/client'
import { render, screen, waitFor } from '@testing-library/react'
import { mockProjectsDashboardOverviewData } from '@unit/data/mockProjectsDashboardOverviewData'
import millify from 'millify'
import ProjectsDashboardPage from 'app/projects/dashboard/page'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: () => ({
    isSyncing: false,
  }),
}))

jest.mock('react-apexcharts', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-apexcharts">Mock ApexChart</div>
    },
  }
})

const mockError = {
  error: new Error('GraphQL error'),
}

describe('ProjectsDashboardOverviewPage', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProjectsDashboardOverviewData,
      loading: false,
      error: null,
    })
  })
  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })
    render(<ProjectsDashboardPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders error state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: mockError,
    })
    render(<ProjectsDashboardPage />)
    const errorMessage = screen.getByText('No project health data available')
    expect(errorMessage).toBeInTheDocument()
  })

  test('renders project health stats', async () => {
    render(<ProjectsDashboardPage />)

    const healthyProjects = screen.getByText(
      mockProjectsDashboardOverviewData.projectHealthStats.projectsCountHealthy.toString()
    )
    const attentionProjects = screen.getByText(
      mockProjectsDashboardOverviewData.projectHealthStats.projectsCountNeedAttention.toString()
    )
    const unhealthyProjects = screen.getByText(
      mockProjectsDashboardOverviewData.projectHealthStats.projectsCountUnhealthy.toString()
    )
    const averageScore = screen.getByText(
      mockProjectsDashboardOverviewData.projectHealthStats.averageScore.toFixed(1)
    )
    const totalContributors = screen.getByText(
      millify(mockProjectsDashboardOverviewData.projectHealthStats.totalContributors)
    )
    const totalForks = screen.getByText(
      millify(mockProjectsDashboardOverviewData.projectHealthStats.totalForks)
    )
    const totalStars = screen.getByText(
      millify(mockProjectsDashboardOverviewData.projectHealthStats.totalStars)
    )
    await waitFor(() => {
      expect(screen.getByText('Project Health Dashboard Overview')).toBeInTheDocument()

      expect(screen.getAllByText('Healthy').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Need Attention').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Unhealthy').length).toBeGreaterThan(0)
      expect(screen.getByText('Average Score')).toBeInTheDocument()
      expect(screen.getByText('Contributors')).toBeInTheDocument()
      expect(screen.getByText('Forks')).toBeInTheDocument()
      expect(screen.getByText('Stars')).toBeInTheDocument()
      expect(screen.getByText('Overall Project Health Monthly Trend')).toBeInTheDocument()
      expect(screen.getByText('Project Health Distribution')).toBeInTheDocument()
      expect(healthyProjects).toBeInTheDocument()
      expect(attentionProjects).toBeInTheDocument()
      expect(unhealthyProjects).toBeInTheDocument()
      expect(averageScore).toBeInTheDocument()
      expect(totalContributors).toBeInTheDocument()
      expect(totalForks).toBeInTheDocument()
      expect(totalStars).toBeInTheDocument()
    })
  })
})
