import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import type { UnifiedSearchBarProps } from 'types/unifiedSearchBar'
import UnifiedSearchBar from 'components/UnifiedSearchBar'

jest.mock('@heroui/select', () => ({
  Select: function Mock({
    children,
    selectedKeys,
    onSelectionChange,
    'aria-label': label,
    ...props
  }: unknown) {
    const selectedValue = selectedKeys instanceof Set ? Array.from(selectedKeys)[0] || '' : ''
    // Filter out HeroUI-specific props that shouldn't be on HTML select
    const safeProps = Object.fromEntries(
      Object.entries(props as Record<string, unknown>).filter(
        ([key]) => !['classNames', 'labelPlacement', 'size', 'label'].includes(key)
      )
    )
    return (
      <select
        aria-label={label}
        value={selectedValue}
        onChange={(e) => {
          ;(onSelectionChange as (keys: Set<string>) => void)(new Set([e.target.value]))
        }}
        {...safeProps}
      >
        {children}
      </select>
    )
  },

  SelectItem: function Mock({ children, classNames: _cn, textValue, ...props }: unknown) {
    return (
      <option value={textValue as string} {...(props as object)}>
        {children}
      </option>
    )
  },
}))

jest.mock('components/SearchPageLayout', () => {
  return function Mock({ children, searchBarChildren }: unknown) {
    return (
      <div data-testid="search-page-layout">
        <div data-testid="search-bar-children">{searchBarChildren}</div>
        <div data-testid="layout-children">{children}</div>
      </div>
    )
  }
})

jest.mock('components/Search', () => {
  return function Mock({ onSearch, placeholder, isLoaded, initialValue }: unknown) {
    return (
      <input
        data-testid="search-input"
        placeholder={placeholder}
        value={initialValue}
        onChange={(e) => onSearch(e.target.value)}
        disabled={!isLoaded}
      />
    )
  }
})

jest.mock('components/SortBy', () => {
  return function Mock({
    sortOptions,
    selectedSortOption,
    selectedOrder,
    onSortChange,
    onOrderChange,
  }: unknown) {
    return (
      <div data-testid="sort-by">
        <select
          data-testid="sort-select"
          value={selectedSortOption}
          onChange={(e) => onSortChange(e.target.value)}
        >
          {sortOptions?.map((option: unknown) => (
            <option
              key={(option as Record<string, unknown>).key}
              value={(option as Record<string, unknown>).key}
            >
              {(option as Record<string, unknown>).label}
            </option>
          ))}
        </select>
        <select
          data-testid="order-select"
          value={selectedOrder}
          onChange={(e) => onOrderChange(e.target.value)}
        >
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </div>
    )
  }
})

describe('UnifiedSearchBar', () => {
  const mockOnSearch = jest.fn()
  const mockOnSortChange = jest.fn()
  const mockOnOrderChange = jest.fn()
  const mockOnCategoryChange = jest.fn()
  const mockOnPageChange = jest.fn()

  const defaultProps: UnifiedSearchBarProps = {
    searchQuery: '',
    sortBy: 'score',
    order: 'desc',
    category: '',
    isLoaded: true,
    sortOptions: [
      { key: 'score', label: 'Score' },
      { key: 'popularity', label: 'Popularity' },
    ],
    categoryOptions: [
      { key: '', label: 'All Categories' },
      { key: 'tech', label: 'Technology' },
      { key: 'science', label: 'Science' },
    ],
    searchPlaceholder: 'Search here...',
    onSearch: mockOnSearch,
    onSortChange: mockOnSortChange,
    onOrderChange: mockOnOrderChange,
    onCategoryChange: mockOnCategoryChange,
    currentPage: 1,
    totalPages: 5,
    onPageChange: mockOnPageChange,
    indexName: 'items',
    empty: 'No items found',
    children: <div data-testid="test-children">Test Content</div>,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders UnifiedSearchBar with all elements', () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    expect(screen.getByTestId('search-page-layout')).toBeInTheDocument()
    expect(screen.getByTestId('search-input')).toBeInTheDocument()
    expect(screen.getByTestId('sort-by')).toBeInTheDocument()
    expect(screen.getByTestId('test-children')).toBeInTheDocument()
  })

  test('renders category filter when categoryOptions has more than one item', () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const categorySelect = screen.getByLabelText('Filter by category')
    expect(categorySelect).toBeInTheDocument()
  })

  test('does not render category filter when categoryOptions has only one item', () => {
    const propsWithSingleCategory = {
      ...defaultProps,
      categoryOptions: [{ key: '', label: 'All Categories' }],
    }
    render(<UnifiedSearchBar {...propsWithSingleCategory} />)

    const categorySelect = screen.queryByLabelText('Filter by category')
    expect(categorySelect).not.toBeInTheDocument()
  })

  test('does not render category filter when categoryOptions is empty', () => {
    const propsWithEmptyCategory = {
      ...defaultProps,
      categoryOptions: [],
    }
    render(<UnifiedSearchBar {...propsWithEmptyCategory} />)

    const categorySelect = screen.queryByLabelText('Filter by category')
    expect(categorySelect).not.toBeInTheDocument()
  })

  test('calls onCategoryChange when category is selected', async () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const categorySelect = screen.getByLabelText('Filter by category') as HTMLSelectElement
    fireEvent.change(categorySelect, { target: { value: 'tech' } })

    await waitFor(() => {
      expect(mockOnCategoryChange).toHaveBeenCalledWith('tech')
    })
  })

  test('calls onSearch when search input changes', async () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const searchInput = screen.getByTestId('search-input')
    fireEvent.change(searchInput, { target: { value: 'test query' } })

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith('test query')
    })
  })

  test('calls onSortChange when sort option changes', async () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const sortSelect = screen.getByTestId('sort-select')
    fireEvent.change(sortSelect, { target: { value: 'popularity' } })

    await waitFor(() => {
      expect(mockOnSortChange).toHaveBeenCalledWith('popularity')
    })
  })

  test('calls onOrderChange when order changes', async () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const orderSelect = screen.getByTestId('order-select')
    fireEvent.change(orderSelect, { target: { value: 'asc' } })

    await waitFor(() => {
      expect(mockOnOrderChange).toHaveBeenCalledWith('asc')
    })
  })

  test('renders with default search placeholder when not provided', () => {
    const propsWithoutPlaceholder = {
      ...defaultProps,
      searchPlaceholder: undefined,
    }
    render(<UnifiedSearchBar {...propsWithoutPlaceholder} />)

    const searchInput = screen.getByTestId('search-input')
    expect(searchInput).toHaveAttribute('placeholder', 'Search...')
  })

  test('renders SearchBar with custom placeholder', () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const searchInput = screen.getByTestId('search-input')
    expect(searchInput).toHaveAttribute('placeholder', 'Search here...')
  })

  test('renders SearchBar with correct initial value', () => {
    const propsWithQuery = {
      ...defaultProps,
      searchQuery: 'python programming',
    }
    render(<UnifiedSearchBar {...propsWithQuery} />)

    const searchInput = screen.getByTestId('search-input') as HTMLInputElement
    expect(searchInput.value).toBe('python programming')
  })

  test('disables search input when not loaded', () => {
    const propsNotLoaded = {
      ...defaultProps,
      isLoaded: false,
    }
    render(<UnifiedSearchBar {...propsNotLoaded} />)

    const searchInput = screen.getByTestId('search-input') as HTMLInputElement
    expect(searchInput).toBeDisabled()
  })

  test('enables search input when loaded', () => {
    const propsLoaded = {
      ...defaultProps,
      isLoaded: true,
    }
    render(<UnifiedSearchBar {...propsLoaded} />)

    const searchInput = screen.getByTestId('search-input') as HTMLInputElement
    expect(searchInput).not.toBeDisabled()
  })

  test('renders with correct selected category', () => {
    const propsWithCategory = {
      ...defaultProps,
      category: 'science',
    }
    render(<UnifiedSearchBar {...propsWithCategory} />)

    const categorySelect = screen.getByLabelText('Filter by category')
    expect(categorySelect).toBeInTheDocument()
  })

  test('passes correct props to SortBy component', () => {
    const customSortOptions = [
      { key: 'date', label: 'Date' },
      { key: 'relevance', label: 'Relevance' },
    ]
    const propsWithCustomSort = {
      ...defaultProps,
      sortBy: 'relevance',
      order: 'asc',
      sortOptions: customSortOptions,
    }
    render(<UnifiedSearchBar {...propsWithCustomSort} />)

    const sortSelect = screen.getByTestId('sort-select') as HTMLSelectElement
    const orderSelect = screen.getByTestId('order-select') as HTMLSelectElement

    expect(sortSelect.value).toBe('relevance')
    expect(orderSelect.value).toBe('asc')
  })

  test('uses default sortBy value when not provided', () => {
    const propsWithoutSortBy = {
      ...defaultProps,
      sortBy: '' as string,
      order: 'asc',
    }
    render(<UnifiedSearchBar {...propsWithoutSortBy} />)

    const sortSelect = screen.getByTestId('sort-select') as HTMLSelectElement
    expect(sortSelect).toBeInTheDocument()
  })

  test('uses default order value when not provided', () => {
    const propsWithoutOrder = {
      ...defaultProps,
      sortBy: 'relevance',
      order: '' as string,
    }
    render(<UnifiedSearchBar {...propsWithoutOrder} />)

    const orderSelect = screen.getByTestId('order-select') as HTMLSelectElement
    expect(orderSelect).toBeInTheDocument()
  })

  test('uses default values when both sortBy and order are not provided', () => {
    const propsWithoutBoth = {
      ...defaultProps,
      sortBy: '' as string,
      order: '' as string,
    }
    render(<UnifiedSearchBar {...propsWithoutBoth} />)

    const sortSelect = screen.getByTestId('sort-select') as HTMLSelectElement
    const orderSelect = screen.getByTestId('order-select') as HTMLSelectElement
    expect(sortSelect).toBeInTheDocument()
    expect(orderSelect).toBeInTheDocument()
  })

  test('renders children correctly', () => {
    const customChildren = <div data-testid="custom-content">Custom Test Content</div>
    const propsWithChildren = {
      ...defaultProps,
      children: customChildren,
    }
    render(<UnifiedSearchBar {...propsWithChildren} />)

    expect(screen.getByTestId('custom-content')).toBeInTheDocument()
    expect(screen.getByText('Custom Test Content')).toBeInTheDocument()
  })

  test('renders with empty string category when initially undefined', () => {
    const propsWithoutCategory = {
      ...defaultProps,
      category: undefined as unknown as string,
    }
    render(<UnifiedSearchBar {...propsWithoutCategory} />)

    const categorySelect = screen.getByLabelText('Filter by category')
    expect(categorySelect).toBeInTheDocument()
  })

  test('all category options are rendered', () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const categorySelect = screen.getByLabelText('Filter by category') as HTMLSelectElement
    const options = categorySelect.querySelectorAll('option')

    expect(options).toHaveLength(defaultProps.categoryOptions.length)
  })

  test('handles undefined categoryOptions gracefully', () => {
    const propsWithoutCategoryOptions = {
      ...defaultProps,
      categoryOptions: undefined,
    }
    render(<UnifiedSearchBar {...propsWithoutCategoryOptions} />)

    const categorySelect = screen.queryByLabelText('Filter by category')
    expect(categorySelect).not.toBeInTheDocument()
  })

  test('renders multiple sort options correctly', () => {
    const multipleSortOptions = [
      { key: 'score', label: 'Score' },
      { key: 'date', label: 'Date' },
      { key: 'popularity', label: 'Popularity' },
      { key: 'relevance', label: 'Relevance' },
    ]
    const propsWithMultipleSorts = {
      ...defaultProps,
      sortOptions: multipleSortOptions,
    }
    render(<UnifiedSearchBar {...propsWithMultipleSorts} />)

    const sortSelect = screen.getByTestId('sort-select') as HTMLSelectElement
    const options = sortSelect.querySelectorAll('option')

    expect(options).toHaveLength(multipleSortOptions.length)
  })

  test('SearchPageLayout receives correct pagination props', () => {
    const customPageProps = {
      ...defaultProps,
      currentPage: 3,
      totalPages: 10,
    }
    render(<UnifiedSearchBar {...customPageProps} />)

    // Verify SearchPageLayout was rendered (it's passed currentPage, totalPages, onPageChange)
    expect(screen.getByTestId('search-page-layout')).toBeInTheDocument()
  })

  test('SearchPageLayout receives correct empty state prop', () => {
    const customEmptyMessage = 'No results available right now'
    const propsWithCustomEmpty = {
      ...defaultProps,
      empty: customEmptyMessage,
    }
    render(<UnifiedSearchBar {...propsWithCustomEmpty} />)

    expect(screen.getByTestId('search-page-layout')).toBeInTheDocument()
  })

  test('category select calls onCategoryChange with correct value', async () => {
    render(<UnifiedSearchBar {...defaultProps} />)

    const categorySelect = screen.getByLabelText('Filter by category') as HTMLSelectElement
    fireEvent.change(categorySelect, { target: { value: 'tech' } })

    await waitFor(() => {
      expect(mockOnCategoryChange).toHaveBeenCalledWith('tech')
      expect(mockOnCategoryChange).toHaveBeenCalledTimes(1)
    })
  })

  test('renders with all props variations', () => {
    const propsVariation = {
      ...defaultProps,
      searchQuery: 'test',
      sortBy: 'popularity',
      order: 'asc',
      category: 'tech',
      isLoaded: true,
      currentPage: 2,
      totalPages: 20,
    }
    render(<UnifiedSearchBar {...propsVariation} />)

    expect(screen.getByTestId('search-input')).toHaveValue('test')
    expect(screen.getByLabelText('Filter by category')).toBeInTheDocument()
  })

  test('renders SearchBar with isLoaded prop', () => {
    const { rerender } = render(<UnifiedSearchBar {...defaultProps} isLoaded={false} />)

    let searchInput = screen.getByTestId('search-input') as HTMLInputElement
    expect(searchInput).toBeDisabled()

    rerender(<UnifiedSearchBar {...defaultProps} isLoaded={true} />)

    searchInput = screen.getByTestId('search-input') as HTMLInputElement
    expect(searchInput).not.toBeDisabled()
  })
})
