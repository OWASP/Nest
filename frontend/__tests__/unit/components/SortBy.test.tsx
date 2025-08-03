import { render, screen, fireEvent } from '@testing-library/react'
import { act } from 'react-dom/test-utils'
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
    const select = screen.getByLabelText('Sort By :')
    expect(select).toBeInTheDocument()
    expect(select).toHaveValue('name')
  })

  it('renders all options and selects the correct one', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    const select = screen.getByLabelText('Sort By :')
    expect(select).toHaveValue('name')
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Date')).toBeInTheDocument()
  })

  it('calls onSortChange when a different option is selected', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    await act(async () => {
      fireEvent.change(screen.getByLabelText('Sort By :'), { target: { value: 'date' } })
    })
    expect(defaultProps.onSortChange).toHaveBeenCalledWith('date')
  })

  it('renders ascending icon and tooltip when order is "asc"', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="asc" />)
    })
    // Look for a button with a title or aria-label containing "ascending"
    const orderBtn = screen.getByRole('button', { name: /ascending/i })
    expect(orderBtn).toBeInTheDocument()
  })

  it('renders descending icon and tooltip when order is "desc"', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="desc" />)
    })
    // Look for a button with a title or aria-label containing "descending" 
    const orderBtn = screen.getByRole('button', { name: /descending/i })
    expect(orderBtn).toBeInTheDocument()
  })

  it('toggles order when the button is clicked', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} selectedOrder="asc" />)
    })
    await act(async () => {
      // Get the sort order button by its role and partial name match
      const orderBtn = screen.getByRole('button', { name: /ascending/i })
      fireEvent.click(orderBtn)
    })
    expect(defaultProps.onOrderChange).toHaveBeenCalledWith('desc')
  })

  it('uses proper accessibility attributes', async () => {
    await act(async () => {
      render(<SortBy {...defaultProps} />)
    })
    const select = screen.getByLabelText('Sort By :')
    expect(select.tagName).toBe('SELECT')
    
    // Get button by role with a more flexible matcher
    const orderBtn = screen.getByRole('button', { name: /order|sort/i })
    expect(orderBtn).toHaveAttribute('aria-label')
  })
})
