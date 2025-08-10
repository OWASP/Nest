import { useQuery } from '@apollo/client'
import { render, screen, waitFor } from '@testing-library/react'
import { mockProjectsDashboardMetricsDetailsData } from '@unit/data/mockProjectsDashboardMetricsDetailsData'
import ProjectHealthMetricsDetails from 'app/projects/dashboard/metrics/[projectKey]/page'

jest.mock('react-apexcharts', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-apexcharts">Mock ApexChart</div>
    },
  }
})
jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
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

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon"></span>,
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('ProjectHealthMetricsDetails', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProjectsDashboardMetricsDetailsData,
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
    render(<ProjectHealthMetricsDetails />)
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
      headers.forEach((header) => {
        expect(screen.getByText(header)).toBeInTheDocument()
      })
      expect(screen.getByText(metrics.projectName)).toBeInTheDocument()
      expect(screen.getByText(metrics.score.toString())).toBeInTheDocument()
    })
  })
})
