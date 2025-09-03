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
    const sortIcon = screen.getByRole('img', { hidden: true })
    expect(sortIcon.classList.contains('fa-arrow-up-wide-short')).toBe(true)
  })

  it('renders descending icon and tooltip when order is "desc"', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="desc" />)
    })
    // Look for the icon that indicates descending order
    const sortIcon = screen.getByRole('img', { hidden: true })
    expect(sortIcon.classList.contains('fa-arrow-down-wide-short')).toBe(true)
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
})
