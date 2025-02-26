import { useQuery } from '@apollo/client'
import { screen, waitFor } from '@testing-library/react'
import { mockChapterDetailsData } from '@unit/data/mockChapterDetailsData'
import { ChapterDetailsPage } from 'pages'
import { render } from 'wrappers/testUtil'
jest.mock('hooks/useToast', () => ({
  toast: jest.fn(),
}))

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    chapterKey: 'test-chapter',
  }),
}))

describe('chapterDetailsPage Component', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { chapter: mockChapterDetailsData },
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: null,
    })
    render(<ChapterDetailsPage />)
    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders chapter data correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { chapter: mockChapterDetailsData },
      error: null,
    })
    render(<ChapterDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test City, Test Country')).toBeInTheDocument()
    })
    expect(screen.getByText('Test Region')).toBeInTheDocument()
    expect(screen.getByText('https://owasp.org/test-chapter')).toBeInTheDocument()
    expect(screen.getByText('This is a test chapter summary.')).toBeInTheDocument()
  })

  test('displays "No chapters found" when there are no chapters', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      error: true,
    })
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
      topContributors: [
        {
          name: 'user1',
          avatarUrl: 'https://example.com/avatar1.jpg',
          contributionsCount: 30,
        },
      ],
    }
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { chapter: chapterDataWithIncompleteContributors },
      error: null,
    })
    render(<ChapterDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument()
    })
  })
})
