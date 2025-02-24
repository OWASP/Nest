import { fireEvent, screen, waitFor } from '@testing-library/react'

import { mockChapterData } from '@unit/data/mockChapterData'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useNavigate } from 'react-router-dom'
import { render } from 'wrappers/testUtil'

import ChaptersPage from 'pages/Chapters'

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))
jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange }) => (
    <div>
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ))
)

describe('ChaptersPage Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockChapterData.chapters,
      totalPages: 2,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders skeleton initially', async () => {
    render(<ChaptersPage />)
    await waitFor(() => {
      const skeletonLoaders = screen.getAllByRole('status')
      expect(skeletonLoaders.length).toBeGreaterThan(0)
    })
  })

  test('renders chapter data correctly', async () => {
    render(<ChaptersPage />)
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Chapter 1.')).toBeInTheDocument()
    const viewButton = screen.getByText('View Details')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "No chapters found" when there are no chapters', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [], totalPages: 0 })
    render(<ChaptersPage />)
    await waitFor(() => {
      expect(screen.getByText('No chapters found')).toBeInTheDocument()
    })
  })

  test('handles page change correctly', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockChapterData.chapters,
      totalPages: 2,
    })
    render(<ChaptersPage />)
    await waitFor(() => {
      const nextPageButton = screen.getByText('Next Page')
      fireEvent.click(nextPageButton)
    })
    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'auto',
    })
  })

  test('renders SearchBar, data, and pagination component concurrently after data is loaded', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockChapterData.chapters,
      totalPages: 2,
    })
    render(<ChaptersPage />)

    const skeletonLoaders = screen.getAllByRole('status')
    await waitFor(() => {
      expect(skeletonLoaders.length).toBeGreaterThan(0)
      expect(screen.queryByText('Next Page')).not.toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for OWASP chapters...')).toBeInTheDocument()
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
      expect(screen.getByText('Next Page')).toBeInTheDocument()
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
  })
  test('opens  window on View Details button click', async () => {
    const navigateMock = jest.fn()
    ;(useNavigate as jest.Mock).mockReturnValue(navigateMock)

    render(<ChaptersPage />)

    await waitFor(() => {
      const contributeButton = screen.getByText('View Details')
      expect(contributeButton).toBeInTheDocument()
      fireEvent.click(contributeButton)
    })

    //suppose index_key is chapter_1
    expect(navigateMock).toHaveBeenCalledWith('/chapters/chapter_1')

    // Clean up the mock
    jest.restoreAllMocks()
  })
})
