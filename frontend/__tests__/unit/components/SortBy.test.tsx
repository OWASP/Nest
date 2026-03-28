import { render, screen, fireEvent } from '@testing-library/react'
import { act } from 'react'
import SortBy from 'components/SortBy'

describe('<SortBy />', () => {
  /** Select trigger is always the first button; order toggle is second when visible. */
  const getSortTrigger = () => screen.getAllByRole('button')[0]

  const defaultProps = {
    sortOptions: [
      { label: 'Name', key: 'name' },
      { label: 'Date', key: 'date' },
    ],
    selectedSortOption: 'name',
    onSortChange: jest.fn(),
    selectedOrder: 'asc',
    onOrderChange: jest.fn(),
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders successfully with minimal required props', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    const sortTrigger = getSortTrigger()
    expect(sortTrigger).toHaveAttribute('aria-label', 'Sort by')
    expect(sortTrigger).toBeInTheDocument()
    const selectedOption = screen.getByText('Name', { selector: '[data-slot="value"]' })
    expect(selectedOption).toBeInTheDocument()
  })

  it('renders all options and selects the correct one', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    const sortTrigger = getSortTrigger()
    await act(async () => {
      sortTrigger.click()
    })
    expect(await screen.findByRole('option', { name: 'Name' })).toBeInTheDocument()
    expect(await screen.findByRole('option', { name: 'Date' })).toBeInTheDocument()
  })

  it('calls onSortChange when a different option is selected', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    await act(async () => {
      const hiddenSelect = screen.getByRole('combobox', { hidden: true })
      fireEvent.change(hiddenSelect, { target: { value: 'date' } })
    })
    expect(defaultProps.onSortChange).toHaveBeenCalledWith('date')
  })

  it('renders ascending icon and tooltip when order is "asc"', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="asc" />)
    })
    // Look for the icon that indicates ascending order
    const sortIcon = screen.getByLabelText(/Sort in ascending order/i).querySelector('svg')
    expect(sortIcon).toBeInTheDocument()
  })

  it('renders descending icon and tooltip when order is "desc"', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="desc" />)
    })
    // Look for the icon that indicates descending order
    const sortIcon = screen.getByLabelText(/Sort in descending order/i).querySelector('svg')
    expect(sortIcon).toBeInTheDocument()
  })

  it('toggles order when the button is clicked', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="asc" />)
    })
    await act(async () => {
      // Get the second button (the sort order button)
      const buttons = screen.getAllByRole('button')
      fireEvent.click(buttons[1])
    })
    expect(defaultProps.onOrderChange).toHaveBeenCalledWith('desc')
  })

  it('toggles order from desc to asc when the button is clicked', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="desc" />)
    })
    await act(async () => {
      const buttons = screen.getAllByRole('button')
      fireEvent.click(buttons[1])
    })
    expect(defaultProps.onOrderChange).toHaveBeenCalledWith('asc')
  })

  it('uses proper accessibility attributes', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    expect(hiddenSelect.tagName).toBe('SELECT')

    const sortTrigger = getSortTrigger()
    expect(sortTrigger).toHaveAttribute('aria-label', 'Sort by')
    const container = sortTrigger.closest('div')
    expect(container).toBeInTheDocument()
  })

  it('toggles order when Enter key is pressed on sort order button', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="asc" />)
    })
    await act(async () => {
      const buttons = screen.getAllByRole('button')
      const orderButton = buttons[1]
      fireEvent.keyDown(orderButton, { key: 'Enter' })
    })
    expect(defaultProps.onOrderChange).toHaveBeenCalledWith('desc')
  })

  it('toggles order when Space key is pressed on sort order button', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="desc" />)
    })
    await act(async () => {
      const buttons = screen.getAllByRole('button')
      const orderButton = buttons[1]
      fireEvent.keyDown(orderButton, { key: ' ' })
    })
    expect(defaultProps.onOrderChange).toHaveBeenCalledWith('asc')
  })

  it('does not toggle order when other keys are pressed on order button', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="asc" />)
    })
    await act(async () => {
      const orderButton = screen.getByLabelText(/Sort in ascending order/i)
      fireEvent.keyDown(orderButton, { key: 'Tab' })
    })
    expect(defaultProps.onOrderChange).not.toHaveBeenCalled()
  })

  it('returns null when sortOptions is empty', () => {
    const { container } = render(<SortBy {...defaultProps} sortOptions={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('returns null when sortOptions is undefined', () => {
    const { container } = render(<SortBy {...defaultProps} sortOptions={undefined} />)
    expect(container.firstChild).toBeNull()
  })

  it('hides sort order button when selectedSortOption is "default"', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="default" />)
    })
    const orderButtons = screen.queryByLabelText(/Sort in ascending order/i)
    expect(orderButtons).not.toBeInTheDocument()
  })

  it('does not render order button when selectedSortOption is default', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="default" />)
    })
    const sortOrderButton = screen.queryByLabelText(/Sort in/i)
    expect(sortOrderButton).not.toBeInTheDocument()
  })

  it('renders sort dropdown and order button connected with no gap', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="name" selectedOrder="asc" />)
    })
    const container = getSortTrigger().closest('.flex.items-center')
    expect(container).toBeInTheDocument()
    expect(container).not.toHaveClass('gap-2')
  })

  it('renders order button with matching height to dropdown', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="name" selectedOrder="asc" />)
    })
    const orderButton = screen.getByLabelText(/Sort in ascending order/i)
    expect(orderButton).toHaveClass('h-12')
  })

  it('renders dropdown wrapper with rounded-r-none when order button is visible', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="name" selectedOrder="asc" />)
    })
    const sortButton = getSortTrigger()
    const outerWrapper = sortButton.closest('.h-12.items-center')
    expect(outerWrapper).toHaveClass('rounded-r-none')
    expect(outerWrapper).toHaveClass('border-r-0')
  })

  it('renders dropdown wrapper with full rounded-lg when order button is hidden', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="default" />)
    })
    // When no option is selected the order button is hidden; only the Select trigger is present
    const sortButton = screen.getByRole('button')
    const outerWrapper = sortButton.closest('.h-12.items-center')
    expect(outerWrapper).toHaveClass('rounded-lg')
    expect(outerWrapper).not.toHaveClass('rounded-r-none')
  })

  it('renders order button with rounded-l-none for seamless connection', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="name" selectedOrder="asc" />)
    })
    const orderButton = screen.getByLabelText(/Sort in ascending order/i)
    expect(orderButton).toHaveClass('rounded-l-none')
    expect(orderButton).toHaveClass('rounded-r-lg')
    expect(orderButton).toHaveClass('border-l-0')
  })

  it('renders order button without focus ring', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedSortOption="name" selectedOrder="asc" />)
    })
    const orderButton = screen.getByLabelText(/Sort in ascending order/i)
    expect(orderButton).toHaveClass('focus:ring-0')
    expect(orderButton).toHaveClass('focus:ring-offset-0')
  })
})
