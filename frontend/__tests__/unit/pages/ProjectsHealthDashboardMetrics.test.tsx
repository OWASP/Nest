import { useQuery } from '@apollo/client'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
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

jest.mock('components/ProjectsDashboardDropDown', () => ({
  __esModule: true,
  default: ({ onAction, sections }) => (
    <div>
      {sections.map((section) => (
        <div key={section.title}>
          <h3>{section.title}</h3>
          {section.items.map((item) => (
            <button key={item.key} onClick={() => onAction(item.key)}>
              {item.label}
            </button>
          ))}
        </div>
      ))}
    </div>
  ),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: () => ({
    isSyncing: false,
  }),
}))

jest.mock('@heroui/react', () => ({
  ...jest.requireActual('@heroui/react'),
  Pagination: ({ page, onChange }) => (
    <div>
      <button onClick={() => onChange(page + 1)}>Next Page</button>
    </div>
  ),
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
    await waitFor(() => {
      expect(errorMessage).toBeInTheDocument()
    })
  })

  test('renders page header', async () => {
    render(<MetricsPage />)
    const header = screen.getByRole('heading', { name: 'Project Health Metrics' })
    await waitFor(() => {
      expect(header).toBeInTheDocument()
    })
  })
  test('renders metrics table headers', async () => {
    const headers = ['Project Name', 'Stars', 'Forks', 'Contributors', 'Health Checked At', 'Score']
    render(<MetricsPage />)
    await waitFor(() => {
      headers.forEach((header) => {
        expect(screen.getAllByText(header).length).toBeGreaterThan(0)
      })
    })
  })
  test('renders filter and sort dropdowns', async () => {
    render(<MetricsPage />)
    const filterOptions = [
      'Incubator',
      'Lab',
      'Production',
      'Flagship',
      'Healthy',
      'Need Attention',
      'Unhealthy',
      'Reset All Filters',
    ]
    const filterSectionsLabels = ['Project Level', 'Project Health', 'Reset Filters']
    const sortOptions = ['Ascending', 'Descending']

    await waitFor(() => {
      filterSectionsLabels.forEach((label) => {
        expect(screen.getAllByText(label).length).toBeGreaterThan(0)
      })
      filterOptions.forEach((option) => {
        expect(screen.getAllByText(option).length).toBeGreaterThan(0)
        const button = screen.getByRole('button', { name: option })
        fireEvent.click(button)
        expect(button).toBeInTheDocument()
      })
      sortOptions.forEach((option) => {
        expect(screen.getAllByText(option).length).toBeGreaterThan(0)
        const button = screen.getByRole('button', { name: option })
        fireEvent.click(button)
        expect(button).toBeInTheDocument()
      })
    })
  })
  test('render health metrics data', async () => {
    render(<MetricsPage />)
    const metrics = mockHealthMetricsData.projectHealthMetrics
    await waitFor(() => {
      expect(metrics.length).toBeGreaterThan(0)

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
  test('handles pagination', async () => {
    const mockFetchMore = jest.fn()

    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const nextPageButton = screen.getByText('Next Page')
    expect(nextPageButton).toBeInTheDocument()
    fireEvent.click(nextPageButton)
  })
})
