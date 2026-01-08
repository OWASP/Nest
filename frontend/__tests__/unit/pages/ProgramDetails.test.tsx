import { useQuery } from '@apollo/client/react'
import { screen, waitFor } from '@testing-library/react'
import mockProgramDetailsData from '@unit/data/mockProgramData'
import { render } from 'wrappers/testUtil'
import ProgramDetailsPage from 'app/mentorship/programs/[programKey]/page'
import '@testing-library/jest-dom'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(() => [jest.fn()]),
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: () => ({ replace: jest.fn() }),
  useParams: () => ({ programKey: 'test-program' }),
  useSearchParams: () => new URLSearchParams(),
}))

describe('ProgramDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProgramDetailsData,
      loading: false,
      refetch: jest.fn(),
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner when loading', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: true,
      data: null,
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
    })
  })

  test('renders 404 if no program found', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: { program: null },
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Program Not Found')).toBeInTheDocument()
    })
  })

  test('renders program details correctly', async () => {
    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
      expect(screen.getByText('Sample summary')).toBeInTheDocument()
      expect(screen.getByText('Draft')).toBeInTheDocument()
      expect(screen.getByText('Jan 1, 2025')).toBeInTheDocument()
      expect(screen.getByText('Dec 31, 2025')).toBeInTheDocument()
      expect(screen.getByText('20')).toBeInTheDocument()
      expect(screen.getByText('Beginner, Intermediate')).toBeInTheDocument()
    })
  })
})
