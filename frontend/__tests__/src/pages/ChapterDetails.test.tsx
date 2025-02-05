import { screen, waitFor } from '@testing-library/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { ChapterDetailsPage } from 'pages'
import { render } from 'wrappers/testUtil'
import { mockChapterDetailsData } from '@tests/data/mockChapterDetailsData'
jest.mock('api/fetchAlgoliaData')

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    chapterKey: 'test-chapter',
  }),
}))

describe('chapterDetailsPage Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        hits: [mockChapterDetailsData],
      })
    )
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
      expect(screen.getByText('Test City, Test Country')).toBeInTheDocument()
    })
    expect(screen.getByText('Test Region')).toBeInTheDocument()
    expect(screen.getByText('https://owasp.org/test-chapter')).toBeInTheDocument()
    expect(screen.getByText('This is a test chapter summary.')).toBeInTheDocument()
  })

  test('displays "No chapters found" when there are no chapters', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [], totalPages: 0 })
    render(<ChapterDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Chapter not found')).toBeInTheDocument()
    })
  })

  test('contributors visibility check', async () => {
    render(<ChapterDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
    })
    expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
  })

  test('renders chapter URL as clickable link', async () => {
    render(<ChapterDetailsPage />)

    await waitFor(() => {
      const link = screen.getByText('https://owasp.org/test-chapter')
      expect(link.tagName).toBe('A')
      expect(link).toHaveAttribute('href', 'https://owasp.org/test-chapter')
    })
  })

  test('handles contributors with missing names gracefully', async () => {
    const chapterDataWithIncompleteContributors = {
      ...mockChapterDetailsData,
      top_contributors: [
        {
          name: 'user1',
          avatar_url: 'https://example.com/avatar1.jpg',
          contributions_count: 30,
        },
      ],
    }

    ;(fetchAlgoliaData as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        hits: [chapterDataWithIncompleteContributors],
      })
    )

    render(<ChapterDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument()
    })
  })
})
