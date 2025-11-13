import { useQuery } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import { mockChapterDetailsData } from '@unit/data/mockChapterDetailsData'
import { render } from 'wrappers/testUtil'
import ChapterDetailsPage from 'app/chapters/[chapterKey]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    chapterKey: 'test-chapter',
  }),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ chapterKey: 'test-chapter' }),
}))

describe('chapterDetailsPage Component', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockChapterDetailsData,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner initially', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
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
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockChapterDetailsData,
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
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { chapter: null },
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
    expect(screen.getByText('Contributor 10')).toBeInTheDocument()
    expect(screen.getByText('Contributor 12')).toBeInTheDocument()
    expect(screen.queryByText('Contributor 13')).not.toBeInTheDocument()
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
          login: 'contributor1',
          name: '',
          avatarUrl: 'https://example.com/avatar1.jpg',
        },
      ],
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: chapterDataWithIncompleteContributors,
      error: null,
    })
    render(<ChapterDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Contributor1')).toBeInTheDocument()
    })
  })
  test('renders chapter sponsor block correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockChapterDetailsData,
      error: null,
    })
    render(<ChapterDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText(`Want to become a sponsor?`)).toBeInTheDocument()
      expect(screen.getByText(`Sponsor ${mockChapterDetailsData.chapter.name}`)).toBeInTheDocument()
    })
  })

  test('renders leaders block from entityLeaders', async () => {
    render(<ChapterDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Leaders')).toBeInTheDocument()
      expect(screen.getByText('Bob')).toBeInTheDocument()
      expect(screen.getByText('Chapter Leader')).toBeInTheDocument()
    })
  })
})
