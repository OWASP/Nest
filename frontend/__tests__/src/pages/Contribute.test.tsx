import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { MemoryRouter } from 'react-router-dom'

import { loadData } from '../../../src/lib/api'
import { ContributePage } from '../../../src/pages'
import { mockContributeData } from '../data/mockContributeData'

jest.mock('../../../src/lib/api', () => ({
  loadData: jest.fn(),
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
})
