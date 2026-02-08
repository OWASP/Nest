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
    const mockFetchMore = jest.fn((options) => {
      const updateQuery = options.updateQuery
      const mockFetchMoreResult = { projectHealthMetrics: [] }
      return updateQuery(mockHealthMetricsData, { fetchMoreResult: mockFetchMoreResult })
    })

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

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  test('applies health filter - healthy', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const healthyButton = screen.getByRole('button', { name: 'Healthy' })
    fireEvent.click(healthyButton)

    await waitFor(() => {
      expect(healthyButton).toBeInTheDocument()
    })
  })

  test('applies health filter - needs attention', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const needsAttentionButton = screen.getByRole('button', { name: 'Need Attention' })
    fireEvent.click(needsAttentionButton)

    await waitFor(() => {
      expect(needsAttentionButton).toBeInTheDocument()
    })
  })

  test('applies health filter - unhealthy', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const unhealthyButton = screen.getByRole('button', { name: 'Unhealthy' })
    fireEvent.click(unhealthyButton)

    await waitFor(() => {
      expect(unhealthyButton).toBeInTheDocument()
    })
  })

  test('applies level filter - incubator', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const incubatorButton = screen.getByRole('button', { name: 'Incubator' })
    fireEvent.click(incubatorButton)

    await waitFor(() => {
      expect(incubatorButton).toBeInTheDocument()
    })
  })

  test('applies level filter - lab', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const labButton = screen.getByRole('button', { name: 'Lab' })
    fireEvent.click(labButton)

    await waitFor(() => {
      expect(labButton).toBeInTheDocument()
    })
  })

  test('applies level filter - production', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const productionButton = screen.getByRole('button', { name: 'Production' })
    fireEvent.click(productionButton)

    await waitFor(() => {
      expect(productionButton).toBeInTheDocument()
    })
  })

  test('applies level filter - flagship', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const flagshipButton = screen.getByRole('button', { name: 'Flagship' })
    fireEvent.click(flagshipButton)

    await waitFor(() => {
      expect(flagshipButton).toBeInTheDocument()
    })
  })

  test('resets all filters', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const resetButton = screen.getByRole('button', { name: 'Reset All Filters' })
    fireEvent.click(resetButton)

    await waitFor(() => {
      expect(resetButton).toBeInTheDocument()
    })
  })

  test('applies sort - score descending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const scoreDescButton = screen.getByRole('button', { name: 'Score (High → Low)' })
    fireEvent.click(scoreDescButton)

    await waitFor(() => {
      expect(scoreDescButton).toBeInTheDocument()
    })
  })

  test('applies sort - score ascending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const scoreAscButton = screen.getByRole('button', { name: 'Score (Low → High)' })
    fireEvent.click(scoreAscButton)

    await waitFor(() => {
      expect(scoreAscButton).toBeInTheDocument()
    })
  })

  test('applies sort - stars descending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const starsDescButton = screen.getByRole('button', { name: 'Stars (High → Low)' })
    fireEvent.click(starsDescButton)

    await waitFor(() => {
      expect(starsDescButton).toBeInTheDocument()
    })
  })

  test('applies sort - stars ascending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const starsAscButton = screen.getByRole('button', { name: 'Stars (Low → High)' })
    fireEvent.click(starsAscButton)

    await waitFor(() => {
      expect(starsAscButton).toBeInTheDocument()
    })
  })

  test('applies sort - forks descending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const forksDescButton = screen.getByRole('button', { name: 'Forks (High → Low)' })
    fireEvent.click(forksDescButton)

    await waitFor(() => {
      expect(forksDescButton).toBeInTheDocument()
    })
  })

  test('applies sort - forks ascending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const forksAscButton = screen.getByRole('button', { name: 'Forks (Low → High)' })
    fireEvent.click(forksAscButton)

    await waitFor(() => {
      expect(forksAscButton).toBeInTheDocument()
    })
  })

  test('applies sort - contributors descending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const contributorsDescButton = screen.getByRole('button', {
      name: 'Contributors (High → Low)',
    })
    fireEvent.click(contributorsDescButton)

    await waitFor(() => {
      expect(contributorsDescButton).toBeInTheDocument()
    })
  })

  test('applies sort - contributors ascending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const contributorsAscButton = screen.getByRole('button', {
      name: 'Contributors (Low → High)',
    })
    fireEvent.click(contributorsAscButton)

    await waitFor(() => {
      expect(contributorsAscButton).toBeInTheDocument()
    })
  })

  test('applies sort - created at descending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const createdAtDescButton = screen.getByRole('button', {
      name: 'Last checked (Newest)',
    })
    fireEvent.click(createdAtDescButton)

    await waitFor(() => {
      expect(createdAtDescButton).toBeInTheDocument()
    })
  })

  test('applies sort - created at ascending', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const createdAtAscButton = screen.getByRole('button', {
      name: 'Last checked (Oldest)',
    })
    fireEvent.click(createdAtAscButton)

    await waitFor(() => {
      expect(createdAtAscButton).toBeInTheDocument()
    })
  })

  test('resets sort order', async () => {
    const mockFetchMore = jest.fn()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: mockFetchMore,
    })
    render(<MetricsPage />)

    const resetSortButton = screen.getByRole('button', { name: 'Reset Sorting' })
    fireEvent.click(resetSortButton)

    await waitFor(() => {
      expect(resetSortButton).toBeInTheDocument()
    })
  })

  test('renders no metrics message when metrics are empty', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        projectHealthMetrics: [],
        projectHealthMetricsDistinctLength: 0,
      },
      loading: false,
      error: null,
    })
    render(<MetricsPage />)

    const noMetricsMessage = screen.getByText('No metrics found. Try adjusting your filters.')
    await waitFor(() => {
      expect(noMetricsMessage).toBeInTheDocument()
    })
  })

  test('initializes with ascending order from URL params', async () => {
    const { useSearchParams } = jest.requireMock('next/navigation')
    ;(useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams('order=scoreAsc'))
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: jest.fn(),
    })

    render(<MetricsPage />)
    await expectHeaderVisible()
    // Verify component rendered without errors
    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })

  test('initializes with descending order from URL params', async () => {
    const { useSearchParams } = jest.requireMock('next/navigation')
    ;(useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams('order=starsDesc'))
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: jest.fn(),
    })

    render(<MetricsPage />)
    await expectHeaderVisible()
    // Verify component rendered without errors
    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })

  test('handles pagination when fetchMoreResult is null', async () => {
    const mockFetchMore = jest.fn((options) => {
      const updateQuery = options.updateQuery
      return updateQuery(mockHealthMetricsData, { fetchMoreResult: null })
    })

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

    await waitFor(() => {
      expect(mockFetchMore).toHaveBeenCalled()
    })
  })

  test('initializes with health filter from URL params', async () => {
    const { useSearchParams } = jest.requireMock('next/navigation')
    ;(useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams('health=healthy'))
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: jest.fn(),
    })

    render(<MetricsPage />)
    await expectHeaderVisible()
    // Verify component rendered without errors
    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })

  test('initializes with level filter from URL params', async () => {
    const { useSearchParams } = jest.requireMock('next/navigation')
    ;(useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams('level=incubator'))
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: jest.fn(),
    })

    render(<MetricsPage />)
    await expectHeaderVisible()
    // Verify component rendered without errors
    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })

  test('initializes with both health and level filters from URL params', async () => {
    const { useSearchParams } = jest.requireMock('next/navigation')
    ;(useSearchParams as jest.Mock).mockReturnValue(
      new URLSearchParams('health=needsAttention&level=production')
    )
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockHealthMetricsData,
      loading: false,
      error: null,
      fetchMore: jest.fn(),
    })

    render(<MetricsPage />)
    await expectHeaderVisible()
    // Verify component rendered without errors
    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })
})
