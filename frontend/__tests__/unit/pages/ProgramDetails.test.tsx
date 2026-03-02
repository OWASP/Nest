import { useQuery } from '@apollo/client/react'
import mockProgramDetailsData from '@mockData/mockProgramData'
import { screen, waitFor } from '@testing-library/react'
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

  test('renders error display when GraphQL request fails', async () => {
    const mockError = new Error('GraphQL error')
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: null,
      error: mockError,
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Error loading program')).toBeInTheDocument()
      expect(
        screen.getByText('An error occurred while loading the program data')
      ).toBeInTheDocument()
    })
  })

  test('renders N/A if experienceLevels is null', async () => {
    const mockDataWithoutLevels = {
      getProgram: { ...mockProgramDetailsData.getProgram, experienceLevels: null },
      getProgramModules: mockProgramDetailsData.getProgramModules,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutLevels,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('N/A')).toBeInTheDocument()
    })
  })

  test('renders program without admins (uses undefined fallback)', async () => {
    const mockDataWithoutAdmins = {
      getProgram: { ...mockProgramDetailsData.getProgram, admins: null },
      getProgramModules: mockProgramDetailsData.getProgramModules,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutAdmins,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })
  })

  test('renders program without domains (uses undefined fallback)', async () => {
    const mockDataWithoutDomains = {
      getProgram: { ...mockProgramDetailsData.getProgram, domains: null },
      getProgramModules: mockProgramDetailsData.getProgramModules,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutDomains,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })
  })

  test('renders program without tags (uses undefined fallback)', async () => {
    const mockDataWithoutTags = {
      getProgram: { ...mockProgramDetailsData.getProgram, tags: null },
      getProgramModules: mockProgramDetailsData.getProgramModules,
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      loading: false,
      data: mockDataWithoutTags,
    })
    render(<ProgramDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })
  })
})
