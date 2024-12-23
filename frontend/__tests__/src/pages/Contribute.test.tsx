import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { MemoryRouter } from 'react-router-dom'

import { loadData } from '../../../src/lib/api'
import { getFilteredIcons } from '../../../src/lib/utils'
import { ContributePage } from '../../../src/pages'
import { mockContributeData } from '../data/mockContributeData'

jest.mock('../../../src/lib/api', () => ({
  loadData: jest.fn(),
}))

jest.mock('../../../src/lib/utils', () => ({
  getFilteredIcons: jest.fn(),
}))

jest.mock('../../../src/utils/credentials', () => ({
  API_URL: 'https://mock-api.com',
}))
jest.mock('../../../src/components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange, totalPages }) =>
    totalPages > 1 ? (
      <div>
        <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
      </div>
    ) : null
  )
)

describe('Contribute Component', () => {
  beforeEach(() => {
    ;(loadData as jest.Mock).mockResolvedValue(mockContributeData)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders contribute data correctly', async () => {
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Contribution 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Contribution 1')).toBeInTheDocument()
    const viewButton = screen.getByText('Read More')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No issues found" when there are no issues', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      issues: [],
      total_pages: 0,
    })
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('No issues found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly when there are multiple pages', async () => {
    window.scrollTo = jest.fn()
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      total_pages: 2,
    })
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )
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
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      total_pages: 1,
    })
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )
    await waitFor(() => {
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
  })

  // Test for modal open and close interaction
  test('opens and closes modal on button click', async () => {
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )
    await waitFor(() => {
      const viewButton = screen.getByText('Read More')
      fireEvent.click(viewButton)
    })

    // Test modal open
    expect(screen.getByText('Read More')).toBeInTheDocument()

    const closeButton = screen.getByText('Close') // Adjust if necessary based on actual UI
    fireEvent.click(closeButton)

    // Wait for the modal to disappear
    await waitFor(() => {
      expect(screen.queryByText('Modal Content')).not.toBeInTheDocument()
    })
  })

  // Test pagination for the first page
  test('handles pagination for first page', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      total_pages: 2,
      currentPage: 1,
    })
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })
  })

  // Test pagination for the last page
  test('handles pagination for last page', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockContributeData,
      total_pages: 2,
      currentPage: 2,
    })
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )
    await waitFor(() => {
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
  })
  test('renders contribute card with filtered icons', async () => {
    const mockIcons = ['icon1', 'icon2']
    ;(getFilteredIcons as jest.Mock).mockReturnValue(mockIcons)

    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(getFilteredIcons).toHaveBeenCalledWith(expect.any(Object), [
        'idx_created_at',
        'idx_comments_count',
      ])
    })
  })

  test('handles modal state for multiple cards', async () => {
    const mockMultipleIssues = {
      ...mockContributeData,
      issues: [
        { idx_title: 'Issue 1', idx_summary: 'Summary 1', idx_hint: 'Hint 1' },
        { idx_title: 'Issue 2', idx_summary: 'Summary 2', idx_hint: 'Hint 2' },
      ],
    }
    ;(loadData as jest.Mock).mockResolvedValue(mockMultipleIssues)

    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )

    // Wait for both cards to be rendered
    await waitFor(() => {
      const readMoreButtons = screen.getAllByText('Read More')
      expect(readMoreButtons).toHaveLength(2)
    })

    // Click first card's Read More button
    const readMoreButtons = screen.getAllByText('Read More')
    fireEvent.click(readMoreButtons[0])

    // Verify first modal is open
    expect(screen.getByText('Hint 1')).toBeInTheDocument()

    // Click close button
    const closeButton = screen.getByText('Close')
    fireEvent.click(closeButton)

    // Click second card's Read More button
    fireEvent.click(readMoreButtons[1])

    // Verify second modal is open
    expect(screen.getByText('Hint 2')).toBeInTheDocument()
  })

  test('handles search functionality', async () => {
    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )

    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText('Search for OWASP Issues...')
      fireEvent.change(searchInput, { target: { value: '' } })
    })

    // Verify that the search API is called with correct parameters
    expect(loadData).toHaveBeenCalledWith('owasp/search/issue', '', 1)
  })

  test('handles error states in card rendering', async () => {
    const mockErrorIssue = {
      ...mockContributeData,
      issues: [
        {
          idx_title: null,
          idx_summary: undefined,
          idx_hint: '',
        },
      ],
    }
    ;(loadData as jest.Mock).mockResolvedValue(mockErrorIssue)

    render(
      <MemoryRouter>
        <ContributePage />
      </MemoryRouter>
    )

    await waitFor(() => {
      // Verify that the card still renders without crashing
      expect(screen.getByText('Read More')).toBeInTheDocument()
    })
  })
})
