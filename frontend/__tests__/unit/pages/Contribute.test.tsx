import { mockContributeData } from '@mockData/mockContributeData'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import ContributePage from 'app/contribute/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
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

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useSearchParams: () => new URLSearchParams(),
}))

describe('Contribute Component', () => {
  let mockRouter: { push: jest.Mock }
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockContributeData)
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders skeleton initially', async () => {
    render(<ContributePage />)
    await waitFor(() => {
      const skeletonLoaders = screen.getAllByRole('status')
      expect(skeletonLoaders.length).toBeGreaterThan(0)
    })
  })

  test('renders contribute data correctly', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    })
    render(<ContributePage />)

    await waitFor(() => {
      expect(screen.getByText('Contribution 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Contribution 1')).toBeInTheDocument()
    const viewButton = screen.getByText('Read More')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No issues found" when there are no issues', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      issues: [],
      totalPages: 0,
    })
    render(<ContributePage />)
    await waitFor(() => {
      expect(screen.getByText('No issues found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly when there are multiple pages', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 4,
    })
    render(<ContributePage />)
    await waitFor(() => {
      const nextPageButton = screen.getByText('Next Page')
      fireEvent.click(nextPageButton)
    })
    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'auto',
    })
  })

  test('handles pagination for first page', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockContributeData.issues,
      totalPages: 2,
      currentPage: 1,
    })
    render(<ContributePage />)
    await waitFor(() => {
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })
  })

  test('handles pagination for last page', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      totalPages: 2,
      currentPage: 2,
    })
    render(<ContributePage />)
    await waitFor(() => {
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
  })

  test('does not render pagination when there is only one page', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      totalPages: 1,
    })
    render(<ContributePage />)
    await waitFor(() => {
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
  })

  test('handles search functionality', async () => {
    render(<ContributePage />)

    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText('Search for issues...')
      fireEvent.change(searchInput, { target: { value: '' } })
    })

    expect(fetchAlgoliaData).toHaveBeenCalledWith('issues', '', 1, undefined)
  })

  test('handles error states in card rendering', async () => {
    const mockErrorIssue = {
      ...mockContributeData,
      issues: [
        {
          title: null,
          summary: undefined,
          hint: '',
        },
      ],
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockErrorIssue)

    render(<ContributePage />)

    await waitFor(() => {
      expect(screen.queryByText('Read More')).not.toBeInTheDocument()
    })
  })

  test('renders SubmitButton correctly', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    })
    render(<ContributePage />)

    await waitFor(() => {
      const readMoreButton = screen.getByText('Read More')
      expect(readMoreButton).toBeInTheDocument()
    })
  })

  test('opens modal when SubmitButton is clicked', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    })
    render(<ContributePage />)

    await waitFor(() => {
      const readMoreButton = screen.getByText('Read More')
      fireEvent.click(readMoreButton)
    })

    await waitFor(() => {
      const modalTitle = screen.getByText('Close')
      expect(modalTitle).toBeInTheDocument()
    })
  })

  test('closes modal when close button is clicked', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    })
    render(<ContributePage />)

    await waitFor(() => {
      const readMoreButton = screen.getByText('Read More')
      fireEvent.click(readMoreButton)
    })

    await waitFor(() => {
      const closeButton = screen.getByText('Close')
      fireEvent.click(closeButton)
    })

    // After closing, the Read More button should be visible again
    expect(screen.getByText('Read More')).toBeInTheDocument()
  })

  test('renders View Issue button in modal', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    })
    render(<ContributePage />)

    await waitFor(() => {
      const readMoreButton = screen.getByText('Read More')
      fireEvent.click(readMoreButton)
    })

    await waitFor(() => {
      const viewIssueButton = screen.getByText('View Issue')
      expect(viewIssueButton).toBeInTheDocument()
    })
  })
})
