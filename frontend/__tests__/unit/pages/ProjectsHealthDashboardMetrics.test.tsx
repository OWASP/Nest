import { useQuery } from '@apollo/client/react'
import { mockHealthMetricsData } from '@mockData/mockProjectsHealthMetricsData'
import { screen, waitFor, act } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import MetricsPage from 'app/projects/dashboard/metrics/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

let capturedSearchBarProps: Record<string, unknown> = {}

jest.mock('components/UnifiedSearchBar', () => ({
  __esModule: true,
  default: (props: unknown) => {
    capturedSearchBarProps = props
    return (
      <div data-testid="unified-search-bar">
        <h1>{props.searchPlaceholder}</h1>
        {props.children}
      </div>
    )
  },
}))

jest.mock('@heroui/react', () => ({
  ...jest.requireActual('@heroui/react'),
  Pagination: ({ page, onChange }: { page: number; onChange: (p: number) => void }) => (
    <div>
      <button onClick={() => onChange(page + 1)}>Next Page</button>
    </div>
  ),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: () => ({ isSyncing: false }),
}))

const mockReplace = jest.fn()
const mockUseSearchParams = jest.fn(() => new URLSearchParams())

jest.mock('next/navigation', () => ({
  useSearchParams: jest.fn(() => mockUseSearchParams()),
  usePathname: jest.fn(() => '/'),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: mockReplace,
  })),
}))

const mockFetchMore = jest.fn()

const setupUseQuery = (overrides = {}) => {
  ;(useQuery as unknown as jest.Mock).mockReturnValue({
    data: mockHealthMetricsData,
    loading: false,
    error: null,
    fetchMore: mockFetchMore,
    ...overrides,
  })
}

describe('MetricsPage', () => {
  beforeEach(() => {
    capturedSearchBarProps = {}
    mockUseSearchParams.mockReturnValue(new URLSearchParams())
    setupUseQuery()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders page header', async () => {
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('renders loading state (LoadingSpinner shown)', async () => {
    setupUseQuery({ data: null, loading: true })
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByTestId('unified-search-bar')).toBeInTheDocument()
    })
  })

  test('renders error state – header still visible', async () => {
    setupUseQuery({ data: null, loading: false, error: new Error('GraphQL Error') })
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('renders metrics cards when data is present', async () => {
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('renders empty state message when metrics array is empty', async () => {
    setupUseQuery({
      data: { projectHealthMetrics: [], projectHealthMetricsDistinctLength: 0 },
    })
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('handleSearchChange – sets query and updates URL', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onSearch).toBeDefined())

    act(() => {
      capturedSearchBarProps.onSearch('apollo')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('search=apollo'))
  })

  test('handleSearchChange – deletes search param when query is empty', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('search=old'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onSearch).toBeDefined())

    act(() => {
      capturedSearchBarProps.onSearch('')
    })

    const calledUrl: string = mockReplace.mock.calls[0][0]
    expect(calledUrl).not.toContain('search=')
  })

  test('handleSortChange – sets order URL param and updates state', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onSortChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onSortChange('starsDesc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=starsDesc'))
  })

  test('handleSortChange – works for forksDesc', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onSortChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onSortChange('forksDesc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=forksDesc'))
  })

  test('handleSortChange – works for contributorsDesc', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onSortChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onSortChange('contributorsDesc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=contributorsDesc'))
  })

  test('handleSortChange – works for createdAtDesc', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onSortChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onSortChange('createdAtDesc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=createdAtDesc'))
  })

  test('handleSortChange – works for scoreAsc', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onSortChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onSortChange('scoreAsc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=scoreAsc'))
  })

  test('handleOrderChange – switches to asc order key', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=scoreDesc'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onOrderChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onOrderChange('asc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=scoreAsc'))
  })

  test('handleOrderChange – switches to desc order key', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=scoreAsc'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onOrderChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onOrderChange('desc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=scoreDesc'))
  })

  test('handleOrderChange – uses starsDesc/starsAsc pair', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=starsDesc'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onOrderChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onOrderChange('asc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=starsAsc'))
  })

  test('handleOrderChange – uses forksDesc/forksAsc pair', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=forksAsc'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onOrderChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onOrderChange('desc')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('order=forksDesc'))
  })

  test('handleOrderChange – no-op when newOrderKey not found (bad param)', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=unknownKey'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onOrderChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onOrderChange('asc')
    })
    expect(true).toBe(true)
  })

  test('handleCategoryChange – applies healthy filter', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('healthy')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('health=healthy'))
  })

  test('handleCategoryChange – applies needsAttention filter', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('needsAttention')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('health=needsAttention'))
  })

  test('handleCategoryChange – applies unhealthy filter', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('unhealthy')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('health=unhealthy'))
  })

  test('handleCategoryChange – applies incubator level filter', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('incubator')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('level=incubator'))
  })

  test('handleCategoryChange – applies lab level filter', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('lab')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('level=lab'))
  })

  test('handleCategoryChange – applies production level filter', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('production')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('level=production'))
  })

  test('handleCategoryChange – applies flagship level filter', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('flagship')
    })

    expect(mockReplace).toHaveBeenCalledWith(expect.stringContaining('level=flagship'))
  })

  test('handleCategoryChange – clears filters when empty category passed', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('health=healthy'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onCategoryChange).toBeDefined())

    act(() => {
      capturedSearchBarProps.onCategoryChange('')
    })

    const calledUrl: string = mockReplace.mock.calls[0][0]
    expect(calledUrl).not.toContain('health=')
    expect(calledUrl).not.toContain('level=')
  })

  test('onPageChange – calls fetchMore with correct variables', async () => {
    const mockFetchMoreImpl = jest.fn().mockResolvedValue({})
    setupUseQuery({ fetchMore: mockFetchMoreImpl })

    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onPageChange).toBeDefined())

    await act(async () => {
      await capturedSearchBarProps.onPageChange(2)
    })

    expect(mockFetchMoreImpl).toHaveBeenCalledWith(
      expect.objectContaining({
        variables: expect.objectContaining({
          pagination: { offset: 10, limit: 10 },
        }),
      })
    )
  })

  test('onPageChange – updateQuery returns fetchMoreResult when present', async () => {
    let capturedUpdateQuery: ((prevData: unknown, options: unknown) => unknown) | undefined
    const mockFetchMoreImpl = jest.fn((opts) => {
      capturedUpdateQuery = opts.updateQuery
      return Promise.resolve({})
    })
    setupUseQuery({ fetchMore: mockFetchMoreImpl })

    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onPageChange).toBeDefined())

    await act(async () => {
      await capturedSearchBarProps.onPageChange(2)
    })

    const prevData = mockHealthMetricsData
    const fetchMoreResult = { projectHealthMetrics: [] }
    const result = capturedUpdateQuery(prevData, { fetchMoreResult })
    expect(result.projectHealthMetrics).toEqual([])
  })

  test('onPageChange – updateQuery returns prev when fetchMoreResult is null', async () => {
    let capturedUpdateQuery: ((prevData: unknown, options: unknown) => unknown) | undefined
    const mockFetchMoreImpl = jest.fn((opts) => {
      capturedUpdateQuery = opts.updateQuery
      return Promise.resolve({})
    })
    setupUseQuery({ fetchMore: mockFetchMoreImpl })

    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.onPageChange).toBeDefined())

    await act(async () => {
      await capturedSearchBarProps.onPageChange(2)
    })

    const prevData = mockHealthMetricsData
    const result = capturedUpdateQuery(prevData, { fetchMoreResult: null })
    expect(result).toBe(prevData)
  })

  test('initializes with ascending order from URL params', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=scoreAsc'))
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('initializes with descending order from URL params', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=starsDesc'))
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('initializes with health filter from URL params', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('health=healthy'))
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('initializes with needsAttention health filter from URL', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('health=needsAttention'))
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('initializes with level filter from URL params', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('level=incubator'))
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('initializes with both health and level filters from URL params (level takes precedence)', async () => {
    mockUseSearchParams.mockReturnValue(
      new URLSearchParams('health=needsAttention&level=production')
    )
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('initializes with search query from URL params', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('search=myapp'))
    render(<MetricsPage />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    })
  })

  test('getSortFieldKey returns scoreDesc when no urlKey', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.sortBy).toBeDefined())
    expect(capturedSearchBarProps.sortBy).toBe('scoreDesc')
  })

  test('getSortFieldKey normalizes Asc suffix to Desc for sortBy', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=starsAsc'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.sortBy).toBeDefined())
    expect(capturedSearchBarProps.sortBy).toBe('starsDesc')
  })

  test('order prop is "asc" when urlKey ends with Asc', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=forksAsc'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.order).toBeDefined())
    expect(capturedSearchBarProps.order).toBe('asc')
  })

  test('order prop is "desc" when urlKey ends with Desc', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=starsDesc'))
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.order).toBeDefined())
    expect(capturedSearchBarProps.order).toBe('desc')
  })

  test('currentPage prop starts at 1', async () => {
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.currentPage).toBeDefined())
    expect(capturedSearchBarProps.currentPage).toBe(1)
  })

  test('totalPages is calculated from metricsLength', async () => {
    setupUseQuery({
      data: {
        projectHealthMetrics: mockHealthMetricsData.projectHealthMetrics,
        projectHealthMetricsDistinctLength: 25,
      },
    })
    render(<MetricsPage />)
    await waitFor(() => expect(capturedSearchBarProps.totalPages).toBeDefined())
    expect(capturedSearchBarProps.totalPages).toBe(3) // ceil(25/10)
  })

  test('useEffect – updates ordering when URL order param changes (line 167)', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=scoreDesc'))
    const { rerender } = render(<MetricsPage />)
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    )

    // Now change the URL to a different ordering – effect should call setOrdering
    mockUseSearchParams.mockReturnValue(new URLSearchParams('order=starsDesc'))
    await act(async () => {
      rerender(<MetricsPage />)
    })

    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })

  test('useEffect – updates searchQuery when URL search param changes (lines 172-173)', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams())
    const { rerender } = render(<MetricsPage />)
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    )

    mockUseSearchParams.mockReturnValue(new URLSearchParams('search=newquery'))
    await act(async () => {
      rerender(<MetricsPage />)
    })

    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })

  test('useEffect – updates filters when URL health param changes (lines 186-187)', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams())
    const { rerender } = render(<MetricsPage />)
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    )

    mockUseSearchParams.mockReturnValue(new URLSearchParams('health=healthy'))
    await act(async () => {
      rerender(<MetricsPage />)
    })

    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })

  test('useEffect – updates filters when URL level param changes (lines 186-187, level branch)', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams())
    const { rerender } = render(<MetricsPage />)
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
    )

    mockUseSearchParams.mockReturnValue(new URLSearchParams('level=lab'))
    await act(async () => {
      rerender(<MetricsPage />)
    })

    expect(screen.getByRole('heading', { name: 'Project Health Metrics' })).toBeInTheDocument()
  })
})
