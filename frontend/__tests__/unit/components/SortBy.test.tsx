import { render, screen, fireEvent } from '@testing-library/react'
import { act } from 'react'
import SortBy from 'components/SortBy'

describe('<SortBy />', () => {
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
    const sortButton = screen.getByRole('button', { name: /Sort By/ })
    expect(sortButton).toBeInTheDocument()
    const selectedOption = screen.getByText('Name', { selector: '[data-slot="value"]' })
    expect(selectedOption).toBeInTheDocument()
  })

  it('renders all options and selects the correct one', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    const sortButton = screen.getByRole('button', { name: /Sort By/ })
    await act(async () => {
      sortButton.click()
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

  it('uses proper accessibility attributes', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    expect(hiddenSelect.tagName).toBe('SELECT')

    // Use getAllByText to handle multiple elements with same text
    const sortButton = screen.getByRole('button', { name: /Sort By/ })
    const container = sortButton.closest('div')
    expect(container).toBeInTheDocument()
    expect(hiddenSelect).toHaveAccessibleName(/Sort By/)
  })

  it('toggles order when Enter key is pressed on order button', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="asc" />)
    })
    await act(async () => {
      const orderButton = screen.getByLabelText(/Sort in ascending order/i)
      fireEvent.keyDown(orderButton, { key: 'Enter' })
    })
    expect(defaultProps.onOrderChange).toHaveBeenCalledWith('desc')
  })

  it('toggles order when Space key is pressed on order button', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="desc" />)
    })
    await act(async () => {
      const orderButton = screen.getByLabelText(/Sort in descending order/i)
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
})
