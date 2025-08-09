import { fireEvent, screen, waitFor } from '@testing-library/react'
import { mockPrograms } from '@unit/data/mockProgramData'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import ProgramsPage from 'app/mentorship/programs/page'

import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}
jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useSearchParams: () => new URLSearchParams(),
}))

jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange }) => (
    <div>
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ))
)

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

describe('ProgramsPage Component', () => {
  let mockRouter: { push: jest.Mock }
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockPrograms,
      totalPages: 2,
    })
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders published program cards', async () => {
    render(<ProgramsPage />)

    await waitFor(() => {
      expect(screen.getByText('Program 1')).toBeInTheDocument()
    })

    expect(screen.getByText('This is a summary of Program 1.')).toBeInTheDocument()
    expect(screen.getByText('View Details')).toBeInTheDocument()
  })

  test('shows empty message when no programs found', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [], totalPages: 0 })

    render(<ProgramsPage />)

    await waitFor(() => {
      expect(screen.getByText('No programs found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockPrograms,
      totalPages: 2,
    })
    render(<ProgramsPage />)
    await waitFor(() => {
      const nextPageButton = screen.getByText('Next Page')
      fireEvent.click(nextPageButton)
    })
    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'auto',
    })
  })

  test('navigates to program detail page on View Details click', async () => {
    render(<ProgramsPage />)

    await waitFor(() => {
      const viewButton = screen.getByText('View Details')
      fireEvent.click(viewButton)
    })

    expect(mockRouter.push).toHaveBeenCalledWith('/mentorship/programs/program_1')
  })
})
