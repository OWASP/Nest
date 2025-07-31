import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import SortBy from 'components/SortBy'

describe('<SortBy />', () => {
  const defaultProps = {
    options: [
      { label: 'Name', value: 'name' },
      { label: 'Date', value: 'date' },
    ],
    selected: 'name',
    onChange: jest.fn(),
    selectedOrder: 'asc',
    onOrderChange: jest.fn(),
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders successfully with minimal required props', () => {
    render(<SortBy {...defaultProps} />)
    expect(screen.getByText('Sort by')).toBeInTheDocument()
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('renders all options and selects the correct one', () => {
    render(<SortBy {...defaultProps} />)
    const select = screen.getByRole('combobox')
    expect(select).toHaveValue('name')
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Date')).toBeInTheDocument()
  })

  it('calls onChange when a different option is selected', () => {
    render(<SortBy {...defaultProps} />)
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'date' } })
    expect(defaultProps.onChange).toHaveBeenCalledWith('date')
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
    // Remove onOrderChange and selectedOrder
    const { container } = render(
      <SortBy
        options={defaultProps.options}
        selected="name"
        onChange={defaultProps.onChange}
      />
    )
    expect(container).toBeInTheDocument()
  })

  it('renders correct classNames and structure', () => {
    render(<SortBy {...defaultProps} />)
    const wrapper = screen.getByText('Sort by').closest('div')
    expect(wrapper).toHaveClass('flex', 'items-center')
  })

  it('has accessible labels and roles', () => {
    render(<SortBy {...defaultProps} />)
    expect(screen.getByRole('combobox')).toHaveAccessibleName('Sort by')
    expect(screen.getByRole('button')).toHaveAttribute('aria-label')
  })

  it('handles empty options array', () => {
    render(
      <SortBy
        options={[]}
        selected=""
        onChange={jest.fn()}
      />
    )
    expect(screen.getByRole('combobox').children.length).toBe(0)
  })

  it('handles invalid selected value', () => {
    render(<SortBy {...defaultProps} selected="invalid" />)
    expect(screen.getByRole('combobox')).toHaveValue('invalid')
  })
})