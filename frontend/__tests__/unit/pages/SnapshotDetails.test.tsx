import { useQuery } from '@apollo/client'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { mockSnapshotDetailsData } from '@unit/data/mockSnapshotData'
import { SnapshotDetailsPage } from 'pages'
import { useNavigate } from 'react-router-dom'
import { render } from 'wrappers/testUtil'
import { toaster } from 'components/ui/toaster'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('components/ui/toaster', () => ({
  toaster: {
    create: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ id: '2024-12' }),
  useNavigate: jest.fn(),
}))

const mockError = {
  error: new Error('GraphQL error'),
}

describe('SnapshotDetailsPage', () => {
  let navigateMock: jest.Mock

  beforeEach(() => {
    navigateMock = jest.fn()
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
      loading: false,
      error: null,
    })
    ;(useNavigate as jest.Mock).mockImplementation(() => navigateMock)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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
    ;(useQuery as jest.Mock).mockReturnValue({
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
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: mockError,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => screen.getByText('Snapshot not found'))
    expect(screen.getByText('Snapshot not found')).toBeInTheDocument()
    expect(toaster.create).toHaveBeenCalledWith({
      description: 'Unable to complete the requested operation.',
      title: 'GraphQL Request Failed',
      type: 'error',
    })
  })

  test('navigates to project page when project card is clicked', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })

    const projectCardButton = screen.getAllByRole('button', { name: /View Details/i })[1]
    fireEvent.click(projectCardButton)

    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith('/projects/nest')
    })
  })

  test('navigates to chapter page when chapter card is clicked', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
    })

    render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Sivagangai')).toBeInTheDocument()
    })

    const chapterCardButton = screen.getAllByRole('button', { name: /View Details/i })[0]
    fireEvent.click(chapterCardButton)

    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith('/chapters/sivagangai')
    })
  })

  test('renders new releases correctly', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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
    ;(useQuery as jest.Mock).mockReturnValue({
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
