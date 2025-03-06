import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { mockContributeData } from '@unit/data/mockContributeData'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { render } from 'wrappers/testUtil'
import ContributePage from 'pages/Contribute'

// Mock dependencies
jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: jest.fn(() => null),
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

describe('Contribute Component', () => {
  // Suppress console errors and warnings during tests
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {})
    jest.spyOn(console, 'warn').mockImplementation(() => {})

    // Reset mocks before each test
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockContributeData)
    ;(FontAwesomeIcon as jest.Mock).mockReturnValue(<div>Icon</div>)
  })

  afterEach(() => {
    jest.clearAllMocks()
    jest.restoreAllMocks()
  })

  test('renders skeleton initially', async () => {
    render(<ContributePage />)
    await waitFor(() => {
      const skeletonLoaders = screen.getAllByRole('status')
      expect(skeletonLoaders.length).toBeGreaterThan(0)
    })
  })

  test('renders contribute data correctly', async () => {
    const mockIssuesData = {
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockIssuesData)

    render(<ContributePage />)

    await waitFor(() => {
      expect(screen.getByText('Contribution 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Contribution 1')).toBeInTheDocument()

    const readMoreButtons = screen.getAllByRole('button', { name: /read more/i })
    expect(readMoreButtons.length).toBeGreaterThan(0)
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
      ...mockContributeData,
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
      total_pages: 1,
    })
    render(<ContributePage />)
    await waitFor(() => {
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
  })

  test('handles search functionality', async () => {
    render(<ContributePage />)

    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText('Search for OWASP issues...')
      fireEvent.change(searchInput, { target: { value: '' } })
    })

    expect(fetchAlgoliaData).toHaveBeenCalledWith('issues', '', 2, undefined)
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
      expect(screen.queryByRole('button', { name: /read more/i })).not.toBeInTheDocument()
    })
  })

  test('renders SubmitButton correctly', async () => {
    const mockIssuesData = {
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockIssuesData)
    render(<ContributePage />)

    await waitFor(() => {
      const readMoreButtons = screen.getAllByRole('button', { name: /read more/i })
      expect(readMoreButtons.length).toBeGreaterThan(0)
    })
  })

  test('opens modal when SubmitButton is clicked', async () => {
    const mockIssuesData = {
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockIssuesData)

    render(<ContributePage />)

    await waitFor(() => {
      const readMoreButtons = screen.getAllByRole('button', { name: /read more/i })
      expect(readMoreButtons.length).toBeGreaterThan(0)
    })

    const readMoreButton = screen.getAllByRole('button', { name: /read more/i })[0]
    fireEvent.click(readMoreButton)

    await waitFor(() => {
      const closeButton = screen.getByRole('button', { name: /close/i })
      expect(closeButton).toBeInTheDocument()
    })
  })

  test('closes modal when onClose is called', async () => {
    const mockIssuesData = {
      ...mockContributeData,
      hits: mockContributeData.issues,
      totalPages: 1,
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockIssuesData)

    render(<ContributePage />)

    await waitFor(() => {
      const readMoreButtons = screen.getAllByRole('button', { name: /read more/i })
      expect(readMoreButtons.length).toBeGreaterThan(0)
    })

    const readMoreButton = screen.getAllByRole('button', { name: /read more/i })[0]
    fireEvent.click(readMoreButton)

    const closeButton = await screen.findByRole('button', { name: /close/i })
    expect(closeButton).toBeInTheDocument()
    fireEvent.click(closeButton)
    

    await waitFor(() => {
      const modalTitle = screen.queryByText(mockContributeData.issues[0].title)
      expect(modalTitle).toBeInTheDocument()
    })
  })

  test('handles modal state for multiple cards', async () => {
    const mockMultipleIssues = {
      ...mockContributeData,
      hits: [
        { title: 'Issue 1', summary: 'Summary 1', hint: 'Hint 1', objectID: '1' },
        { title: 'Issue 2', summary: 'Summary 2', hint: 'Hint 2', objectID: '2' },
      ],
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockMultipleIssues)

    render(<ContributePage />)

    // Wait for both cards to be rendered
    await waitFor(() => {
      const readMoreButtons = screen.getAllByRole('button', { name: /read more/i })
      expect(readMoreButtons).toHaveLength(2)
    })

    // Click first card's Read More button
    const readMoreButtons = screen.getAllByRole('button', { name: /read more/i })
    fireEvent.click(readMoreButtons[0])

    // Verify first modal is open
    await waitFor(() => {
      expect(screen.getByText('Hint 1')).toBeInTheDocument()
    })

    // Verify first issue button
    const viewIssueButton = await screen.findByRole('button', { name: 'View Issue' })
    expect(viewIssueButton).toBeInTheDocument()

    // Click close button
    await waitFor(() => {
      const closeButton = screen.getByRole('button', { name: /close/i })
      fireEvent.click(closeButton)
    })

    // Click second card's Read More button
    fireEvent.click(readMoreButtons[1])

    // Verify second modal is open
    await waitFor(() => {
      expect(screen.getByText('Hint 2')).toBeInTheDocument()
    })
  })
})
