import { mockCommitteeData } from '@mockData/mockCommitteeData'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import CommitteesPage from 'app/committees/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

let mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useSearchParams: () => new URLSearchParams(),
}))

jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange, totalPages }) =>
    totalPages > 1 ? (
      <div>
        <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
      </div>
    ) : null
  )
)

jest.mock('@/components/MarkdownWrapper', () => {
  return ({ content, className }: { content: string; className?: string }) => (
    <div
      className={`md-wrapper ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  )
})

describe('Committees Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockCommitteeData.committees,
      totalPages: 2,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders skeleton initially', async () => {
    render(<CommitteesPage />)
    await waitFor(() => {
      const skeletonLoaders = screen.getAllByRole('status')
      expect(skeletonLoaders.length).toBeGreaterThan(0)
    })
  })

  test('renders SearchBar, data, and pagination component concurrently after data is loaded', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockCommitteeData.committees,
      totalPages: 2,
    })

    render(<CommitteesPage />)

    await waitFor(() => {
      expect(screen.queryByRole('status')).not.toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for committees...')).toBeInTheDocument()
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  test('renders committee data correctly', async () => {
    render(<CommitteesPage />)

    await waitFor(() => {
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Committee 1.')).toBeInTheDocument()
    const viewButton = screen.getByText('View Details')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No committees found" when there are no committees', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [],
      totalPages: 0,
    })
    render(<CommitteesPage />)
    await waitFor(() => {
      expect(screen.getByText('No committees found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly when there are multiple pages', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockCommitteeData.committees,
      totalPages: 2,
    })
    render(<CommitteesPage />)
    await waitFor(() => {
      const nextPageButton = screen.getByText('Next Page')
      fireEvent.click(nextPageButton)
    })
    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'auto',
    })
  })

  test('does not render pagination when there is only one page', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockCommitteeData.committees,
      totalPages: 1,
    })
    render(<CommitteesPage />)
    await waitFor(() => {
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
  })

  test('opens  window on View Details button click', async () => {
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)

    render(<CommitteesPage />)

    await waitFor(() => {
      const contributeButton = screen.getByText('View Details')
      expect(contributeButton).toBeInTheDocument()
      fireEvent.click(contributeButton)
    })
    //suppose index_key is committee_1
    expect(mockRouter.push).toHaveBeenCalledWith('/committees/committee_1')
  })

  test('renders committee card without summary (uses empty string fallback)', async () => {
    const committeeWithoutSummary = {
      ...mockCommitteeData.committees[0],
      summary: undefined,
      key: 'committee_no_summary',
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [committeeWithoutSummary],
      totalPages: 1,
    })

    render(<CommitteesPage />)

    await waitFor(() => {
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
    })
    // Should render without crashing even when summary is undefined
  })
})
