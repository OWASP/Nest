import { fireEvent, render, screen } from '@testing-library/react'

import PaginationButtons from 'components/PaginationButtons'

describe('PaginationButtons', () => {
  const defaultProps = {
    onShowMore: jest.fn(),
    onShowLess: jest.fn(),
    showMore: true,
    showLess: false,
    isLoading: false,
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders nothing when both showMore and showLess are false', () => {
    const { container } = render(
      <PaginationButtons {...defaultProps} showMore={false} showLess={false} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders Show more button when showMore is true', () => {
    render(<PaginationButtons {...defaultProps} />)
    expect(screen.getByText('Show more')).toBeInTheDocument()
    expect(screen.queryByText('Show less')).not.toBeInTheDocument()
  })

  it('renders Show less button when showLess is true', () => {
    render(<PaginationButtons {...defaultProps} showMore={false} showLess={true} />)
    expect(screen.getByText('Show less')).toBeInTheDocument()
    expect(screen.queryByText('Show more')).not.toBeInTheDocument()
  })

  it('renders both buttons when showMore and showLess are true', () => {
    render(<PaginationButtons {...defaultProps} showMore={true} showLess={true} />)
    expect(screen.getByText('Show more')).toBeInTheDocument()
    expect(screen.getByText('Show less')).toBeInTheDocument()
  })

  it('calls onShowMore when Show more button is clicked', () => {
    const onShowMore = jest.fn()
    render(<PaginationButtons {...defaultProps} onShowMore={onShowMore} />)
    fireEvent.click(screen.getByText('Show more'))
    expect(onShowMore).toHaveBeenCalledTimes(1)
  })

  it('calls onShowLess when Show less button is clicked', () => {
    const onShowLess = jest.fn()
    render(
      <PaginationButtons
        {...defaultProps}
        showMore={false}
        showLess={true}
        onShowLess={onShowLess}
      />
    )
    fireEvent.click(screen.getByText('Show less'))
    expect(onShowLess).toHaveBeenCalledTimes(1)
  })

  it('shows Loading... text when isLoading is true', () => {
    render(<PaginationButtons {...defaultProps} isLoading={true} />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.queryByText('Show more')).not.toBeInTheDocument()
  })

  it('disables Show more button when isLoading is true', () => {
    render(<PaginationButtons {...defaultProps} isLoading={true} />)
    const button = screen.getByText('Loading...').closest('button')
    expect(button).toBeDisabled()
  })

  it('disables Show less button when isLoading is true', () => {
    render(
      <PaginationButtons {...defaultProps} showMore={false} showLess={true} isLoading={true} />
    )
    const button = screen.getByText('Show less').closest('button')
    expect(button).toBeDisabled()
  })

  it('enables Show more button when isLoading is false', () => {
    render(<PaginationButtons {...defaultProps} isLoading={false} />)
    const button = screen.getByText('Show more').closest('button')
    expect(button).not.toBeDisabled()
  })

  it('sets aria-expanded attribute on buttons matching expansion state', () => {
    const { rerender } = render(<PaginationButtons {...defaultProps} showLess={false} />)
    expect(screen.getByRole('button', { name: /show more/i })).toHaveAttribute(
      'aria-expanded',
      'false'
    )

    rerender(<PaginationButtons {...defaultProps} showLess={true} />)
    expect(screen.getByRole('button', { name: /show more/i })).toHaveAttribute(
      'aria-expanded',
      'true'
    )

    rerender(<PaginationButtons {...defaultProps} isExpanded={true} />)
    expect(screen.getByRole('button', { name: /show more/i })).toHaveAttribute(
      'aria-expanded',
      'true'
    )
  })
})
