import { fireEvent, screen, waitFor } from '@testing-library/react'

import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useNavigate } from 'react-router-dom'
import { render } from 'wrappers/testUtil'

import CommitteesPage from 'pages/Committees'
import { mockCommitteeData } from '@tests/data/mockCommitteeData'

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
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
      const skeletonLoaders = screen.getAllByTestId('skeleton-loader')
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
      expect(screen.queryByTestId('skeleton-loader')).not.toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for OWASP committees...')).toBeInTheDocument()
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })
    expect(screen.queryByTestId('skeleton-loader')).not.toBeInTheDocument()
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
    const navigateMock = jest.fn()
    ;(useNavigate as jest.Mock).mockReturnValue(navigateMock)

    render(<CommitteesPage />)

    await waitFor(() => {
      const contributeButton = screen.getByText('View Details')
      expect(contributeButton).toBeInTheDocument()
      fireEvent.click(contributeButton)
    })
    //suppose index_key is committee_1
    expect(navigateMock).toHaveBeenCalledWith('/committees/committee_1')
  })
})
