import { within, render, fireEvent, screen, cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'
import Pagination from 'components/Pagination'

afterEach(cleanup)

describe('<Pagination />', () => {
  const onPageChange = jest.fn()

  const renderComponent = (
    overrides: {
      currentPage?: number
      totalPages?: number
      isLoaded?: boolean
    } = {}
  ) => {
    const props = {
      currentPage: overrides.currentPage ?? 1,
      totalPages: overrides.totalPages ?? 5,
      isLoaded: overrides.isLoaded ?? true,
      onPageChange,
    }
    return render(<Pagination {...props} />)
  }

  beforeEach(() => {
    onPageChange.mockClear()
  })

  it('does not render when isLoaded is false', () => {
    const { container } = renderComponent({ isLoaded: false })
    expect(container.firstChild).toBeNull()
  })

  it('does not render when totalPages ≤ 1', () => {
    const { container } = renderComponent({ totalPages: 1 })
    expect(container.firstChild).toBeNull()
  })

  it('renders Prev and Next buttons and page numbers for small totalPages', () => {
    renderComponent({ currentPage: 2, totalPages: 4 })

    // Prev / Next
    const prev = screen.getByRole('button', { name: 'Prev' })
    const next = screen.getByRole('button', { name: 'Next' })

    expect(prev).toBeEnabled()
    expect(next).toBeEnabled()

    // Pages 1–4
    for (let n = 1; n <= 4; n++) {
      expect(screen.getByRole('button', { name: String(n) })).toBeInTheDocument()
    }
  })

  it('disables Prev on first page', () => {
    const { container } = renderComponent({ currentPage: 1, totalPages: 3 })
    const prevBtn = within(container).getByRole('button', { name: 'Prev' })
    expect(prevBtn).toBeDisabled()
  })

  it('disables Next on last page', () => {
    const { container } = renderComponent({ currentPage: 3, totalPages: 3 })
    const nextBtn = within(container).getByRole('button', { name: 'Next' })
    expect(nextBtn).toBeDisabled()
  })

  it('calls onPageChange with correct page number on button clicks', () => {
    renderComponent({ currentPage: 2, totalPages: 5 })

    fireEvent.click(screen.getByRole('button', { name: 'Prev' }))
    expect(onPageChange).toHaveBeenCalledWith(1)

    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(onPageChange).toHaveBeenCalledWith(3)

    fireEvent.click(screen.getByRole('button', { name: '4' }))
    expect(onPageChange).toHaveBeenCalledWith(4)
  })

  it('renders ellipses and correct pages for large totalPages', () => {
    renderComponent({ currentPage: 10, totalPages: 20 })

    // Should show first 3 pages
    for (const n of [1, 2, 3]) {
      expect(screen.getByRole('button', { name: String(n) })).toBeInTheDocument()
    }

    // Should show exactly two “More pages” indicators
    const ellipses = screen.getAllByLabelText('More pages')
    expect(ellipses).toHaveLength(2)

    // Should show pages around currentPage: 9, 10, 11
    for (const n of [9, 10, 11]) {
      expect(screen.getByRole('button', { name: String(n) })).toBeInTheDocument()
    }

    // Last page
    expect(screen.getByRole('button', { name: '20' })).toBeInTheDocument()
  })

  it('applies active styles and aria-current on the selected page', () => {
    renderComponent({ currentPage: 3, totalPages: 5 })

    const activeBtn = screen.getByRole('button', { name: '3' })
    // check for class used in active state
    expect(activeBtn).toHaveClass('bg-[#83a6cc]')
    // accessibility: mark current page
    expect(activeBtn).toHaveAttribute('aria-current', 'page')
  })

  it('uses default values when props are missing', () => {
    // No overrides → currentPage=1, totalPages=5, isLoaded=true
    renderComponent()

    expect(screen.getByRole('button', { name: 'Prev' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Next' })).toBeEnabled()
    expect(screen.getByRole('button', { name: '5' })).toBeInTheDocument()
  })

  // Edge-case: currentPage near the start of a large set
  it('shows correct pages when currentPage = 4 of 10', () => {
    renderComponent({ currentPage: 4, totalPages: 10 })
    // Should show 1,2,3,4,5 then ellipsis and 10
    for (const n of [1, 2, 3, 4, 5]) {
      expect(screen.getByRole('button', { name: String(n) })).toBeInTheDocument()
    }

    expect(screen.getByRole('button', { name: '10' })).toBeInTheDocument()
  })

  // Edge-case: very small totalPages (2)
  it('renders exactly pages [1, 2] when totalPages = 2', () => {
    renderComponent({ totalPages: 2, currentPage: 2 })
    expect(screen.getAllByRole('button', { name: /^(1|2)$/ })).toHaveLength(2)
  })
})
