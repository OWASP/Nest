import { fireEvent, screen, waitFor } from '@testing-library/react'
import React from 'react'

import '@testing-library/jest-dom'
import { loadData } from '../../../src/lib/api'
import { render } from '../../../src/lib/test-util'
import { CommitteesPage } from '../../../src/pages'
import { mockCommitteeData } from '../data/mockCommitteeData'

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
describe('Committees Component', () => {
  beforeEach(() => {
    ;(loadData as jest.Mock).mockResolvedValue(mockCommitteeData)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(<CommitteesPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders SearchBar, data, and pagination component concurrently after data is loaded', async () => {
    window.scrollTo = jest.fn()
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockCommitteeData,
      total_pages: 2,
    })

    render(<CommitteesPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
      expect(
        screen.queryByPlaceholderText('Search for OWASP committees...')
      ).not.toBeInTheDocument()
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for OWASP committees...')).toBeInTheDocument()

      expect(screen.getByText('Committee 1')).toBeInTheDocument()

      const nextPageButton = screen.getByText('Next Page')
      expect(nextPageButton).toBeInTheDocument()

      fireEvent.click(nextPageButton)
    })
    expect(screen.queryByAltText('Loading indicator')).not.toBeInTheDocument()
  })

  test('renders committee data correctly', async () => {
    render(<CommitteesPage />)

    await waitFor(() => {
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Committee 1.')).toBeInTheDocument()
    expect(screen.getByText('Edmond Momartin,')).toBeInTheDocument()
    expect(screen.getByText('Garth Boyd,')).toBeInTheDocument()
    expect(screen.getByText('Kyle Smith')).toBeInTheDocument()
    const viewButton = screen.getByText('Learn More')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No committees found" when there are no committees', async () => {
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockCommitteeData,
      committees: [],
      total_pages: 0,
    })
    render(<CommitteesPage />)
    await waitFor(() => {
      expect(screen.getByText('No committees found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly when there are multiple pages', async () => {
    window.scrollTo = jest.fn()
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockCommitteeData,
      total_pages: 2,
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
    ;(loadData as jest.Mock).mockResolvedValue({
      ...mockCommitteeData,
      total_pages: 1,
    })
    render(<CommitteesPage />)
    await waitFor(() => {
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
  })
})
