import { useQuery } from '@apollo/client/react'
import { mockHealthMetricsData } from '@mockData/mockProjectsHealthMetricsData'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import MetricsPage from 'app/projects/dashboard/metrics/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const createDropDownMockItem = (item, onAction) => (
  <button key={item.key} onClick={() => onAction(item.key)}>
    {item.label}
  </button>
)

const createDropDownMockSection = (section, onAction) => (
  <div key={section.title}>
    <h3>{section.title}</h3>
    {section.items.map((item) => createDropDownMockItem(item, onAction))}
  </div>
)

jest.mock('components/ProjectsDashboardDropDown', () => ({
  __esModule: true,
  default: ({ onAction, sections }) => (
    <div>{sections.map((section) => createDropDownMockSection(section, onAction))}</div>
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

  // Helper functions to reduce nesting depth
  const expectLoadingSpinnerExists = async () => {
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  }

  const expectErrorMessageVisible = async () => {
    const errorMessage = screen.getByText('No metrics found. Try adjusting your filters.')
    await waitFor(() => {
      expect(errorMessage).toBeInTheDocument()
    })
  }

  const expectHeaderVisible = async () => {
    const header = screen.getByRole('heading', { name: 'Project Health Metrics' })
    await waitFor(() => {
      expect(header).toBeInTheDocument()
    })
  }

  const testFilterOptions = async () => {
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
    for (const option of filterOptions) {
      expect(screen.getAllByText(option).length).toBeGreaterThan(0)
      const button = screen.getByRole('button', { name: option })
      fireEvent.click(button)
      expect(button).toBeInTheDocument()
    }
  }

  const testFilterSections = async () => {
    const filterSectionsLabels = ['Project Level', 'Project Health', 'Reset Filters']
    for (const label of filterSectionsLabels) {
      expect(screen.getAllByText(label).length).toBeGreaterThan(0)
    }
  }

  test('renders loading state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })
    render(<MetricsPage />)
    await expectLoadingSpinnerExists()

    expect(true).toBe(true)
  })

  test('renders error state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: graphQLError,
    })
    render(<MetricsPage />)
    await expectErrorMessageVisible()

    expect(true).toBe(true)
  })

  test('renders page header', async () => {
    render(<MetricsPage />)
    await expectHeaderVisible()

    expect(true).toBe(true)
  })

  test('renders filter dropdown', async () => {
    render(<MetricsPage />)
    await waitFor(async () => {
      await testFilterSections()
      await testFilterOptions()
    })

    expect(true).toBe(true)
  })

  const testMetricsDataDisplay = async () => {
    const metrics = mockHealthMetricsData.projectHealthMetrics
    for (const metric of metrics) {
      expect(screen.getAllByText(metric.projectName)[0]).toBeInTheDocument()
      expect(screen.getAllByText(metric.starsCount.toString())[0]).toBeInTheDocument()
      expect(screen.getAllByText(metric.forksCount.toString())[0]).toBeInTheDocument()
      expect(screen.getAllByText(metric.contributorsCount.toString())[0]).toBeInTheDocument()
      expect(
        screen.getAllByText(
          new Date(metric.createdAt).toLocaleString('default', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })
        )[0]
      ).toBeInTheDocument()
      expect(screen.getByText(new RegExp(`Score:.*${metric.score}`))).toBeInTheDocument()
    }
  }

  test('render health metrics data', async () => {
    render(<MetricsPage />)
    await waitFor(async () => {
      const metrics = mockHealthMetricsData.projectHealthMetrics
      expect(metrics.length).toBeGreaterThan(0)
      await testMetricsDataDisplay()
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
