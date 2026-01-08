import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { mockSnapshotDetailsData } from '@unit/data/mockSnapshotData'
import { render } from 'wrappers/testUtil'
import SnapshotDetailsPage from 'app/community/snapshots/[id]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ id: '2024-12' }),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

jest.mock('@/components/MarkdownWrapper', () => {
  return jest.fn(({ content, className }) => (
    <div className={`md-wrapper ${className}`} dangerouslySetInnerHTML={{ __html: content }} />
  ))
})

describe('SnapshotDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    render(<SnapshotDetailsPage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    await waitFor(() => {
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })

  test('renders snapshot details when data is available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Snapshot')).toBeInTheDocument()
    })

    expect(screen.getByText('New Chapters')).toBeInTheDocument()
    expect(screen.getByText('New Projects')).toBeInTheDocument()
    expect(screen.getByText('New Releases')).toBeInTheDocument()
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: mockError,
      loading: false,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => screen.getByText('Error loading snapshot'))
    expect(screen.getByText('Error loading snapshot')).toBeInTheDocument()
    expect(addToast).toHaveBeenCalledWith({
      description: 'An unexpected server error occurred.',
      title: 'Server Error',
      timeout: 5000,
      shouldShowTimeoutProgress: true,
      color: 'danger',
      variant: 'solid',
    })
  })

  test('displays "Snapshot not found" when data is null without error', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      loading: false,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => screen.getByText('Snapshot not found'))
    expect(screen.getByText('Snapshot not found')).toBeInTheDocument()
  })

  test('navigates to project page when project card is clicked', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })

    const projectCardButton = screen.getAllByRole('button', { name: /View Details/i })[1]
    fireEvent.click(projectCardButton)

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/projects/nest')
    })
  })

  test('navigates to chapter page when chapter card is clicked', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Sivagangai')).toBeInTheDocument()
    })

    const chapterCardButton = screen.getAllByRole('button', { name: /View Details/i })[0]
    fireEvent.click(chapterCardButton)

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/chapters/sivagangai')
    })
  })

  test('renders new releases correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Snapshot')).toBeInTheDocument()
      expect(screen.getByText('Latest pre-release')).toBeInTheDocument()
    })

    expect(screen.getByText('test-project-1')).toBeInTheDocument()
    expect(screen.getByText('test-project-2')).toBeInTheDocument()
  })

  test('handles missing data gracefully', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        snapshot: {
          ...mockSnapshotDetailsData.snapshot,
          newChapters: [],
          newProjects: [],
          newReleases: [],
        },
      },
      error: null,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.queryByText('New Chapters')).not.toBeInTheDocument()
      expect(screen.queryByText('New Projects')).not.toBeInTheDocument()
      expect(screen.queryByText('New Releases')).not.toBeInTheDocument()
    })
  })
})
