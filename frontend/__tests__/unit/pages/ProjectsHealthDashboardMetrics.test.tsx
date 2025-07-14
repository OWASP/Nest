import { useQuery } from '@apollo/client'
import { render, screen, waitFor } from '@testing-library/react'
import { mockHealthMetricsData } from '@unit/data/mockProjectsHealthMetricsData'
import MetricsPage from 'app/projects/dashboard/metrics/page'

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

const graphQLError = new Error('GraphQL Error')

jest.mock('next/navigation', () => ({
  useSearchParams: jest.fn(() => ({
    get: jest.fn(),
  })),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
  })),
}))

describe('MetricsPage', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
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
    render(<MetricsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders error state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: graphQLError,
    })
    render(<MetricsPage />)
    const errorMessage = screen.getByText('No metrics found. Try adjusting your filters.')
    expect(errorMessage).toBeInTheDocument()
  })

  test('renders page header', async () => {
    render(<MetricsPage />)
    const header = screen.getByRole('heading', { name: 'Project Health Metrics' })
    const filterButton = screen.getByRole('button', { name: 'Filter By' })
    const sortButton = screen.getByRole('button', { name: 'Sort By' })
    expect(header).toBeInTheDocument()
    expect(filterButton).toBeInTheDocument()
    expect(sortButton).toBeInTheDocument()
  })
  test('renders metrics table headers', async () => {
    const headers = ['Project Name', 'Stars', 'Forks', 'Contributors', 'Health Checked At', 'Score']
    render(<MetricsPage />)
    headers.forEach((header) => {
      expect(screen.getByText(header)).toBeInTheDocument()
    })
  })
  test('render health metrics data', async () => {
    render(<MetricsPage />)
    const metrics = mockHealthMetricsData.projectHealthMetrics
    metrics.forEach((metric) => {
      expect(screen.getByText(metric.projectName)).toBeInTheDocument()
      expect(screen.getByText(metric.starsCount.toString())).toBeInTheDocument()
      expect(screen.getByText(metric.forksCount.toString())).toBeInTheDocument()
      expect(screen.getByText(metric.contributorsCount.toString())).toBeInTheDocument()
      expect(
        screen.getByText(
          new Date(metric.createdAt).toLocaleString('default', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })
        )
      ).toBeInTheDocument()
      expect(screen.getByText(metric.score.toString())).toBeInTheDocument()
    })
  })
})
