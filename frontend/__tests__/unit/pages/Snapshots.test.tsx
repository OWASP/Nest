import { useQuery } from '@apollo/client'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { act } from 'react'
import { useNavigate } from 'react-router-dom'
import { render } from 'wrappers/testUtil'
import { toaster } from 'components/ui/toaster'
import SnapshotsPage from 'pages/Snapshots'

jest.mock('components/ui/toaster', () => ({
  toaster: {
    create: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
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
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { snapshots: mockSnapshots },
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading spinner initially', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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
    ;(useQuery as jest.Mock).mockReturnValue({
      data: { snapshots: [] },
      error: null,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Snapshots found')).toBeInTheDocument()
    })
  })

  it('shows an error toaster when GraphQL request fails', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      error: new Error('GraphQL error'),
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(toaster.create).toHaveBeenCalledWith({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
      })
    })
  })

  it('navigates to the correct URL when "View Snapshot" button is clicked', async () => {
    const navigateMock = jest.fn()
    ;(useNavigate as jest.Mock).mockReturnValue(navigateMock)
    render(<SnapshotsPage />)

    // Wait for the "View Snapshot" button to appear
    const viewSnapshotButton = await screen.findAllByRole('button', { name: /view snapshot/i })

    // Click the button
    await act(async () => {
      fireEvent.click(viewSnapshotButton[0])
    })

    // Check if navigate was called with the correct argument
    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledTimes(1)
      expect(navigateMock).toHaveBeenCalledWith('/community/snapshots/2024-12')
    })
  })
})
