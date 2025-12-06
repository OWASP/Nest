import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { act } from 'react'
import { render } from 'wrappers/testUtil'
import SnapshotsPage from 'app/community/snapshots/page'

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
}))

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockSnapshots = [
  {
    key: '2024-12',
    title: 'Snapshot 1',
    startAt: '2023-01-01T00:00:00Z',
    endAt: '2023-01-02T00:00:00Z',
  },
  {
    key: '2024-11',
    title: 'Snapshot 2',
    startAt: '2022-12-01T00:00:00Z',
    endAt: '2022-12-31T23:59:59Z',
  },
]

describe('SnapshotsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { snapshots: mockSnapshots },
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading spinner initially', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: null,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      const loadingSpinners = screen.getAllByAltText('Loading indicator')
      expect(loadingSpinners.length).toBe(2)
    })
  })

  it('renders snapshots when data is fetched successfully', async () => {
    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.getByText('Snapshot 1')).toBeInTheDocument()
      expect(screen.getByText('Snapshot 2')).toBeInTheDocument()
    })
  })

  it('renders "No Snapshots found" when no snapshots are available', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { snapshots: [] },
      error: null,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Snapshots found')).toBeInTheDocument()
    })
  })

  it('shows an error toaster when GraphQL request fails', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: new Error('GraphQL error'),
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
    })
  })

  it('navigates to the correct URL when "View Snapshot" button is clicked', async () => {
    render(<SnapshotsPage />)

    const viewSnapshotButton = await screen.findAllByRole('button', { name: /view snapshot/i })

    await act(async () => {
      fireEvent.click(viewSnapshotButton[0])
    })

    // Check if navigate was called with the correct argument
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/community/snapshots/2024-12')
    })
  })
})
