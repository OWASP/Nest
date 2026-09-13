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
    const prev = screen.getByRole('button', { name: 'Go to previous page' })
    const next = screen.getByRole('button', { name: 'Go to next page' })

    expect(prev).toBeEnabled()
    expect(next).toBeEnabled()

    // Pages 1–4
    for (let n = 1; n <= 4; n++) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
  })

  it('disables Prev on first page', () => {
    const { container } = renderComponent({ currentPage: 1, totalPages: 3 })
    const prevBtn = within(container).getByRole('button', { name: 'Go to previous page' })
    expect(prevBtn).toBeDisabled()
  })

  it('disables Next on last page', () => {
    const { container } = renderComponent({ currentPage: 3, totalPages: 3 })
    const nextBtn = within(container).getByRole('button', { name: 'Go to next page' })
    expect(nextBtn).toBeDisabled()
  })

  it('calls onPageChange with correct page number on button clicks', () => {
    renderComponent({ currentPage: 2, totalPages: 5 })

    fireEvent.click(screen.getByRole('button', { name: 'Go to previous page' }))
    expect(onPageChange).toHaveBeenCalledWith(1)

    fireEvent.click(screen.getByRole('button', { name: 'Go to next page' }))
    expect(onPageChange).toHaveBeenCalledWith(3)

    fireEvent.click(screen.getByRole('button', { name: 'Go to page 4' }))
    expect(onPageChange).toHaveBeenCalledWith(4)
  })

  it('renders ellipses and correct pages for large totalPages', () => {
    renderComponent({ currentPage: 10, totalPages: 20 })

    for (const n of [1, 2, 9, 10, 11, 19, 20]) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
    expect(screen.queryByRole('button', { name: 'Go to page 3' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Go to page 18' })).not.toBeInTheDocument()

    const ellipsisContainers = document.querySelectorAll('div.flex.h-10.w-10')
    const ellipses = Array.from(ellipsisContainers).filter((el) =>
      el.querySelector('svg[aria-hidden="true"]')
    )
    expect(ellipses).toHaveLength(2)
  })

  it('applies active styles and aria-current on the selected page', () => {
    renderComponent({ currentPage: 3, totalPages: 5 })

    const activeBtn = screen.getByRole('button', { name: 'Go to page 3' })
    // check for class used in active state
    expect(activeBtn).toHaveClass('bg-[#83a6cc]')
    // accessibility: mark current page
    expect(activeBtn).toHaveAttribute('aria-current', 'page')
  })

  it('uses default values when props are missing', () => {
    // No overrides → currentPage=1, totalPages=5, isLoaded=true
    renderComponent()

    expect(screen.getByRole('button', { name: 'Go to previous page' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Go to next page' })).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Go to page 5' })).toBeInTheDocument()
  })

  // Edge-case: currentPage near the start of a large set
  it('shows correct pages when currentPage = 4 of 10', () => {
    renderComponent({ currentPage: 4, totalPages: 10 })

    for (const n of [1, 2, 3, 4, 5, 9, 10]) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
    expect(screen.queryByRole('button', { name: 'Go to page 8' })).not.toBeInTheDocument()

    const ellipsisContainers = document.querySelectorAll('div.flex.h-10.w-10')
    const ellipses = Array.from(ellipsisContainers).filter((el) =>
      el.querySelector('svg[aria-hidden="true"]')
    )
    expect(ellipses).toHaveLength(1)
  })

  // Edge-case: very small totalPages (2)
  it('renders exactly pages [1, 2] when totalPages = 2', () => {
    renderComponent({ totalPages: 2, currentPage: 2 })
    expect(screen.getAllByRole('button', { name: /^Go to page [12]$/ })).toHaveLength(2)
  })

  it('does not render trailing ellipsis when currentPage is near the end', () => {
    renderComponent({ currentPage: 18, totalPages: 20 })

    for (const n of [1, 2, 17, 18, 19, 20]) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
    expect(screen.queryByRole('button', { name: 'Go to page 3' })).not.toBeInTheDocument()

    const ellipsisContainers = document.querySelectorAll('div.flex.h-10.w-10')
    const ellipses = Array.from(ellipsisContainers).filter((el) =>
      el.querySelector('svg[aria-hidden="true"]')
    )
    expect(ellipses).toHaveLength(1)
  })

  it('mirrors start and end ellipsis behavior', () => {
    const { unmount } = renderComponent({ currentPage: 5, totalPages: 20 })

    for (const n of [1, 2, 4, 5, 6, 19, 20]) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
    expect(screen.queryByRole('button', { name: 'Go to page 3' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Go to page 18' })).not.toBeInTheDocument()
    expect(
      Array.from(document.querySelectorAll('div.flex.h-10.w-10')).filter((el) =>
        el.querySelector('svg[aria-hidden="true"]')
      )
    ).toHaveLength(2)

    unmount()
    renderComponent({ currentPage: 16, totalPages: 20 })

    for (const n of [1, 2, 15, 16, 17, 19, 20]) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
    expect(screen.queryByRole('button', { name: 'Go to page 3' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Go to page 18' })).not.toBeInTheDocument()
    expect(
      Array.from(document.querySelectorAll('div.flex.h-10.w-10')).filter((el) =>
        el.querySelector('svg[aria-hidden="true"]')
      )
    ).toHaveLength(2)
  })

  it('shows only a leading ellipsis when the end pages are consecutive', () => {
    renderComponent({ currentPage: 5, totalPages: 8 })

    for (const n of [1, 2, 4, 5, 6, 7, 8]) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
    expect(screen.queryByRole('button', { name: 'Go to page 3' })).not.toBeInTheDocument()

    const ellipsisContainers = document.querySelectorAll('div.flex.h-10.w-10')
    const ellipses = Array.from(ellipsisContainers).filter((el) =>
      el.querySelector('svg[aria-hidden="true"]')
    )
    expect(ellipses).toHaveLength(1)
  })

  it('shows a leading ellipsis when pages 3 and 4 are omitted', () => {
    renderComponent({ currentPage: 6, totalPages: 8 })

    for (const n of [1, 2, 5, 6, 7, 8]) {
      expect(screen.getByRole('button', { name: `Go to page ${n}` })).toBeInTheDocument()
    }
    expect(screen.queryByRole('button', { name: 'Go to page 3' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Go to page 4' })).not.toBeInTheDocument()

    const ellipsisContainers = document.querySelectorAll('div.flex.h-10.w-10')
    const ellipses = Array.from(ellipsisContainers).filter((el) =>
      el.querySelector('svg[aria-hidden="true"]')
    )
    expect(ellipses).toHaveLength(1)
  })
})
