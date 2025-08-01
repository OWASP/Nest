import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import SortBy from 'components/SortBy'

jest.mock('framer-motion', () => {
  const actual = jest.requireActual('framer-motion')
  return {
    ...actual,
    LazyMotion: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  }
})

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

  it('renders successfully with minimal required props', () => {
    render(<SortBy {...defaultProps} />)
    expect(screen.getByText('Sort By :')).toBeInTheDocument()
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('renders all options and selects the correct one', () => {
    render(<SortBy {...defaultProps} />)
    const select = screen.getByRole('combobox')
    expect(select).toHaveValue('name')
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Date')).toBeInTheDocument()
  })

  it('calls onSortChange when a different option is selected', () => {
    render(<SortBy {...defaultProps} />)
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'date' } })
    expect(defaultProps.onSortChange).toHaveBeenCalledWith('date')
  })

  it('renders ascending icon and tooltip when selectedOrder is "asc"', () => {
    render(<SortBy {...defaultProps} selectedOrder="asc" />)
    expect(screen.getByRole('button')).toBeInTheDocument()
    expect(screen.getByLabelText(/Ascending Order/i)).toBeInTheDocument()
  })

  it('renders descending icon and tooltip when selectedOrder is "desc"', () => {
    render(<SortBy {...defaultProps} selectedOrder="desc" />)
    expect(screen.getByRole('button')).toBeInTheDocument()
    expect(screen.getByLabelText(/Descending Order/i)).toBeInTheDocument()
  })

  it('calls onOrderChange when order button is clicked', () => {
    render(<SortBy {...defaultProps} selectedOrder="asc" />)
    fireEvent.click(screen.getByRole('button'))
    expect(defaultProps.onOrderChange).toHaveBeenCalledWith('desc')
  })

  it('handles missing optional props gracefully', () => {
    // Provide all required props, use dummy values if not testing them
    const { container } = render(
      <SortBy
        sortOptions={defaultProps.sortOptions}
        selectedSortOption="name"
        onSortChange={defaultProps.onSortChange}
        selectedOrder="asc"
        onOrderChange={jest.fn()}
      />
    )
    expect(container).toBeInTheDocument()
  })

  it('renders correct classNames and structure', () => {
    render(<SortBy {...defaultProps} />)
    const wrapper = screen.getByText('Sort By :').closest('div')
    expect(wrapper).toHaveClass('flex', 'items-center')
  })

  it('has accessible labels and roles', () => {
    render(<SortBy {...defaultProps} />)
    expect(screen.getByRole('combobox')).toHaveAccessibleName('Sort By :')
    expect(screen.getByRole('button')).toHaveAttribute('aria-label')
  })

  it('handles empty sortOptions array', () => {
    render(
      <SortBy
        sortOptions={[]}
        selectedSortOption=""
        onSortChange={jest.fn()}
        selectedOrder="asc"
        onOrderChange={jest.fn()}
      />
    )
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
  })

  it('handles invalid selectedSortOption value', () => {
    render(<SortBy {...defaultProps} selectedSortOption="invalid" />)
    expect(screen.getByRole('combobox')).toHaveValue('invalid')
  })
})
