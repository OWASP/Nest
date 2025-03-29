import { useQuery } from '@apollo/client'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { toaster } from 'components/ui/toaster'
import  SnapshotsPage  from 'pages/Snapshots'
import { mockSnapshotData, mockSnapshotDetailsData } from '@unit/data/mockSnapshotData'
import { useNavigate } from 'react-router-dom'
import { ChakraProvider } from '@chakra-ui/react'


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
  useNavigate: jest.fn(),
}))

describe('SnapshotsPage', () => {
  let navigateMock: jest.Mock

  beforeEach(() => {
    navigateMock = jest.fn()
    ;(useNavigate as jest.Mock).mockReturnValue(navigateMock)

    // Default mock return value
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockSnapshotData,
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner while fetching data', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      const loadingSpinner = screen.getAllByAltText('Loading indicator')
      expect(loadingSpinner.length).toBeGreaterThan(0)
    })
  })
  test('renders snapshots after data is loaded', async () => {
    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Snapshot')).toBeInTheDocument()
    })
  })

  test('renders loading spinner initially', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      const loadingSpinners = screen.getAllByAltText('Loading indicator')
      expect(loadingSpinners.length).toBeGreaterThan(0)
    })
  })

  test('renders "No Snapshots found" when there are no snapshots', async () => {
    (useQuery as jest.Mock).mockReturnValue({
      data: { snapshots: [] },
      loading: false,
      error: null,
    })

    render(<SnapshotsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Snapshots found')).toBeInTheDocument()
    })
  })

  test('displays error message on GraphQL error', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: false,
      error: new Error('GraphQL Error'),
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
  })


  // test('renders snapshots after data is loaded', async () => {
  //   render(<Snapshots />)

  //   // 🛠️ Wait for snapshots to load
  //   await waitFor(() => {
  //     expect(screen.getByText('New Snapshot')).toBeInTheDocument()
  //   })
  // })

  // test('navigates to snapshot details on button click', async () => {
  //   const navigateMock = jest.fn()
  //   ;(useNavigate as jest.Mock).mockReturnValue(navigateMock)
  //   ;(useQuery as jest.Mock).mockReturnValue({
  //     data: mockSnapshotData,
  //     loading: false,
  //     error: null,
  //   })

  //   render(<Snapshots />)

  //   // Debug DOM if needed
  //   screen.debug()

  //   await waitFor(() => {
  //     expect(screen.getByText('New Snapshot')).toBeInTheDocument()
  //   })

  //   // Find button using role instead of label
  //   const viewButtons = await screen.findAllByRole('button', { name: /view details/i })
  //   expect(viewButtons).toHaveLength(1)

  //   fireEvent.click(viewButtons[0])

  //   expect(navigateMock).toHaveBeenCalledWith('/community/snapshots/2024-12')
  // })

  // test('displays "No Snapshots found" when there are no snapshots', async () => {
  //   // Mocking the return value with no snapshot data
  //   ;(useQuery as jest.Mock).mockReturnValue({
  //     data: { snapshots: [] },
  //     loading: false,
  //     error: null,
  //   })
  //   render(<Snapshots />)

  //   await waitFor(() => {
  //     expect(screen.getByText('No Snapshots found')).toBeInTheDocument()
  //   })
  // })
// })
