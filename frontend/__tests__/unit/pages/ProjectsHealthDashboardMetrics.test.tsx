import { useQuery } from '@apollo/client/react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { mockHealthMetricsData } from '@unit/data/mockProjectsHealthMetricsData'
import MetricsPage from 'app/projects/dashboard/metrics/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
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
  useSearchParams: jest.fn(() => new URLSearchParams()),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
  })),
}))

describe('MetricsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
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
    render(<MetricsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders error state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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
      for (const header of headers) {
        expect(screen.getAllByText(header).length).toBeGreaterThan(0)
      }
    })
  })
  test('renders filter dropdown and sortable column headers', async () => {
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
    const sortableColumns = ['Stars', 'Forks', 'Contributors', 'Health Checked At', 'Score']

    await waitFor(() => {
      for (const label of filterSectionsLabels) {
        expect(screen.getAllByText(label).length).toBeGreaterThan(0)
      }

      for (const option of filterOptions) {
        expect(screen.getAllByText(option).length).toBeGreaterThan(0)
        const button = screen.getByRole('button', { name: option })
        fireEvent.click(button)
        expect(button).toBeInTheDocument()
      }

      for (const column of sortableColumns) {
        const sortButton = screen.getByTitle(`Sort by ${column}`)
        expect(sortButton).toBeInTheDocument()
      }
    })
  })

  test('SortableColumnHeader applies correct alignment classes', async () => {
    render(<MetricsPage />)
    const sortButton = await screen.findByTitle('Sort by Stars')
    const wrapperDiv = sortButton.closest('div')
    expect(wrapperDiv).not.toBeNull()
    expect(wrapperDiv).toHaveClass('justify-center')
    expect(sortButton).toHaveClass('text-center')
  })

  test('handles sorting state and URL updates', async () => {
    const mockReplace = jest.fn()
    const { useRouter, useSearchParams } = jest.requireMock('next/navigation')
    ;(useRouter as jest.Mock).mockReturnValue({
      push: jest.fn(),
      replace: mockReplace,
    })

    // Test unsorted -> descending
    ;(useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams())
    const { rerender } = render(<MetricsPage />)

    const sortButton = screen.getByTitle('Sort by Stars')
    fireEvent.click(sortButton)

    await waitFor(() => {
      const lastCall = mockReplace.mock.calls[mockReplace.mock.calls.length - 1][0]
      const url = new URL(lastCall, 'http://localhost')
      expect(url.searchParams.get('order')).toBe('-stars')
    })

    // Test descending -> ascending
    mockReplace.mockClear()
    ;(useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams('order=-stars'))
    rerender(<MetricsPage />)

    const sortButtonDesc = screen.getByTitle('Sort by Stars')
    fireEvent.click(sortButtonDesc)

    await waitFor(() => {
      const lastCall = mockReplace.mock.calls[mockReplace.mock.calls.length - 1][0]
      const url = new URL(lastCall, 'http://localhost')
      expect(url.searchParams.get('order')).toBe('stars')
    })

    // Test ascending -> unsorted (removes order param, defaults to -score)
    mockReplace.mockClear()
    ;(useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams('order=stars'))
    rerender(<MetricsPage />)

    const sortButtonAsc = screen.getByTitle('Sort by Stars')
    fireEvent.click(sortButtonAsc)

    await waitFor(() => {
      const lastCall = mockReplace.mock.calls[mockReplace.mock.calls.length - 1][0]
      const url = new URL(lastCall, 'http://localhost')
      expect(url.searchParams.get('order')).toBeNull()
    })
  })
  test('render health metrics data', async () => {
    render(<MetricsPage />)
    const metrics = mockHealthMetricsData.projectHealthMetrics
    await waitFor(() => {
      expect(metrics.length).toBeGreaterThan(0)

      for (const metric of metrics) {
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
      }
    })
  })
  test('handles pagination', async () => {
    const mockFetchMore = jest.fn()

    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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
