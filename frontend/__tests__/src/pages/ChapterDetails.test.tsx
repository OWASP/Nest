import { screen, waitFor } from '@testing-library/react'

import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { ChapterDetailsPage } from 'pages'
import { render } from 'wrappers/testUtil'

import { mockChapterData } from '@tests/data/mockChapterData'

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

describe('ChapterDetailsPage Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockChapterData.chapters,
      totalPages: 2,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    render(<ChapterDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders chapter data correctly', async () => {
    render(<ChapterDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Chapter 1.')).toBeInTheDocument()
    expect(screen.getByText('Isanori Sakanashi,')).toBeInTheDocument()
    expect(screen.getByText('Takeshi Murai,')).toBeInTheDocument()
    expect(screen.getByText('Yukiharu Niwa')).toBeInTheDocument()
    const viewButton = screen.getByText('Join')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "Chapter not found" when there are no chapters', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [], totalPages: 0 })
    render(<ChapterDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Chapter not found')).toBeInTheDocument()
    })
  })
})
