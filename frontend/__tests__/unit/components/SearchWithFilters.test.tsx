import { render, screen, fireEvent } from '@testing-library/react'
import { act } from 'react'
import SearchWithFilters from 'components/SearchWithFilters'

jest.mock('lodash/debounce', () => {
  return (fn: (...args: unknown[]) => unknown, delay: number) => {
    let tid: ReturnType<typeof setTimeout>
    const debounced = (...a: unknown[]) => {
      clearTimeout(tid)
      tid = setTimeout(() => fn(...a), delay)
    }
    debounced.cancel = () => clearTimeout(tid)
    return debounced
  }
})

describe('<SearchWithFilters />', () => {
  const defaultProps = {
    isLoaded: true,
    searchQuery: '',
    sortBy: 'default',
    order: 'desc',
    category: '',
    sortOptions: [
      { label: 'Relevancy', key: 'default' },
      { label: 'Stars', key: 'stars_count' },
    ],
    categoryOptions: [
      { label: 'All Types', key: '' },
      { label: 'Code', key: 'idx_type:code' },
      { label: 'Tool', key: 'idx_type:tool' },
    ],
    searchPlaceholder: 'Search for projects...',
    onSearch: jest.fn(),
    onSortChange: jest.fn(),
    onOrderChange: jest.fn(),
    onCategoryChange: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.clearAllTimers()
    jest.useRealTimers()
  })

  describe('Rendering', () => {
    it('renders search input, sort control, and category dropdown', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} />)
      })

      const searchInput = screen.getByPlaceholderText('Search for projects...')
      expect(searchInput).toBeInTheDocument()

      const categorySelect = screen.getByLabelText('Filter by category')
      expect(categorySelect).toBeInTheDocument()

      const sortButton = screen.getByRole('button', { name: /Sort By/ })
      expect(sortButton).toBeInTheDocument()
    })

    it('renders without category dropdown when categoryOptions is not provided', async () => {
      const propsWithoutCategory = {
        ...defaultProps,
        categoryOptions: undefined,
      }
      await act(async () => {
        render(<SearchWithFilters {...propsWithoutCategory} />)
      })

      const searchInput = screen.getByPlaceholderText('Search for projects...')
      expect(searchInput).toBeInTheDocument()

      const categorySelect = screen.queryByLabelText('Filter by category')
      expect(categorySelect).not.toBeInTheDocument()
    })

    it('renders without category dropdown when only one option is provided', async () => {
      const propsWithSingleCategory = {
        ...defaultProps,
        categoryOptions: [{ label: 'All Types', key: '' }],
      }
      await act(async () => {
        render(<SearchWithFilters {...propsWithSingleCategory} />)
      })

      const categorySelect = screen.queryByLabelText('Filter by category')
      expect(categorySelect).not.toBeInTheDocument()
    })
  })

  describe('Search functionality', () => {
    it('calls onSearch when user types in search input', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} />)
      })

      const searchInput = screen.getByPlaceholderText('Search for projects...')
      fireEvent.change(searchInput, { target: { value: 'security' } })

      jest.advanceTimersByTime(750)

      expect(defaultProps.onSearch).toHaveBeenCalledWith('security')
    })
  })

  describe('Sort functionality', () => {
    it('calls onSortChange when sort option is changed', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} />)
      })

      const hiddenSelect = screen.getByRole('combobox', { hidden: true, name: /Sort By/ })
      await act(async () => {
        fireEvent.change(hiddenSelect, { target: { value: 'stars_count' } })
      })

      expect(defaultProps.onSortChange).toHaveBeenCalledWith('stars_count')
    })
  })

  describe('Category functionality', () => {
    it('displays category label', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} />)
      })

      const categoryLabels = screen.getAllByText('Category :')
      expect(categoryLabels.length).toBeGreaterThan(0)
    })

    it('calls onCategoryChange when a category is selected', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} />)
      })

      const trigger = screen.getByRole('button', { name: /Filter by category/i })
      await act(async () => {
        fireEvent.click(trigger)
      })

      const codeOption = await screen.findByRole('option', { name: 'Code' })
      await act(async () => {
        fireEvent.click(codeOption)
      })

      expect(defaultProps.onCategoryChange).toHaveBeenCalledWith('idx_type:code')
    })
  })

  describe('With initial values', () => {
    it('renders with initial search query', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} searchQuery="initial search" />)
      })

      const searchInput = screen.getByPlaceholderText('Search for projects...')
      expect(searchInput).toHaveValue('initial search')
    })
  })

  describe('Default values', () => {
    it('uses default search placeholder when not provided', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} searchPlaceholder={undefined} />)
      })

      const searchInput = screen.getByPlaceholderText('Search...')
      expect(searchInput).toBeInTheDocument()
    })

    it('renders with a selected category value', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} category="idx_type:code" />)
      })

      const categorySelect = screen.getByLabelText('Filter by category')
      expect(categorySelect).toBeInTheDocument()
    })

    it('uses fallback values when sortBy and order are empty', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} sortBy="" order="" />)
      })

      const sortButton = screen.getByRole('button', { name: /Sort By/ })
      expect(sortButton).toBeInTheDocument()
    })

    it('handles empty category selection gracefully', async () => {
      await act(async () => {
        render(<SearchWithFilters {...defaultProps} />)
      })

      const trigger = screen.getByRole('button', { name: /Filter by category/i })
      await act(async () => {
        fireEvent.click(trigger)
      })

      const allTypesOption = await screen.findByRole('option', { name: 'All Types' })
      await act(async () => {
        fireEvent.click(allTypesOption)
      })

      expect(defaultProps.onCategoryChange).toHaveBeenCalled()
    })
  })
})
