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
    startAt: '2023-01-01T00:00:00.000Z',
    endAt: '2023-01-02T00:00:00.000Z',
  },
  {
    key: '2024-11',
    title: 'Snapshot 2',
    startAt: '2022-12-01T00:00:00.000Z',
    endAt: '2022-12-31T23:59:59.000Z',
  },
]

describe('SnapshotsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { snapshots: mockSnapshots, snapshotsCount: 2 },
      error: null,
      loading: false,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading skeletons initially', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      loading: true,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      const loadingSkeletons = screen.getAllByRole('status')
      expect(loadingSkeletons.length).toBeGreaterThan(0)
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
      data: { snapshots: [], snapshotsCount: 0 },
      error: null,
      loading: false,
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
      loading: false,
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

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/community/snapshots/2024-12')
    })
  })

  it('renders date filter inputs', async () => {
    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.getByLabelText('Start date')).toBeInTheDocument()
      expect(screen.getByLabelText('End date')).toBeInTheDocument()
    })
  })

  it('shows clear button when a date filter is set', async () => {
    render(<SnapshotsPage />)

    const startDateInput = screen.getByLabelText('Start date')

    await act(async () => {
      fireEvent.change(startDateInput, { target: { value: '2025-01-01' } })
    })

    await waitFor(() => {
      expect(screen.getByLabelText('Clear date filters')).toBeInTheDocument()
    })
  })

  it('does not show pagination when total pages is 1 or less', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { snapshots: mockSnapshots, snapshotsCount: 2 },
      error: null,
      loading: false,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.queryByLabelText('Go to next page')).not.toBeInTheDocument()
    })
  })

  it('shows pagination when there are more than 12 snapshots', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { snapshots: mockSnapshots, snapshotsCount: 24 },
      error: null,
      loading: false,
    })

    window.scrollTo = jest.fn()

    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.getByLabelText('Go to next page')).toBeInTheDocument()
      expect(screen.getByLabelText('Go to previous page')).toBeInTheDocument()
    })

    await act(async () => {
      fireEvent.click(screen.getByLabelText('Go to next page'))
    })

    await waitFor(() => {
      expect(useQuery).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          variables: expect.objectContaining({
            offset: 12,
          }),
        })
      )
    })
  })

  it('passes filter variables to the query', async () => {
    render(<SnapshotsPage />)

    const startDateInput = screen.getByLabelText('Start date')

    await act(async () => {
      fireEvent.change(startDateInput, { target: { value: '2025-06-01' } })
    })

    await waitFor(() => {
      expect(useQuery).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          variables: expect.objectContaining({
            startAtGte: '2025-06-01T00:00:00',
          }),
        })
      )
    })
  })
})
