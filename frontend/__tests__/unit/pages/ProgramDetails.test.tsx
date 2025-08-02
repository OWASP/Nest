import { useQuery } from '@apollo/client'
import { screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import ProgramDetailsPage from 'app/mentorship/programs/[programKey]/page'
import '@testing-library/jest-dom'
import { ProgramStatusEnum } from 'types/mentorship'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
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
  const mockProgramData = {
    program: {
      key: 'test-program',
      name: 'Test Program',
      description: 'Sample summary',
      status: ProgramStatusEnum.DRAFT,
      startedAt: '2025-01-01',
      endedAt: '2025-12-31',
      menteesLimit: 20,
      experienceLevels: ['beginner', 'intermediate'],
      admins: [{ login: 'admin-user', avatarUrl: 'https://example.com/avatar.png' }],
      tags: ['web', 'security'],
      domains: ['OWASP'],
    },
    getProgramModules: [],
  }

  beforeEach(() => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: mockProgramData,
      loading: false,
      refetch: jest.fn(),
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading spinner when loading', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      loading: true,
      data: null,
    })

    render(<ProgramDetailsPage />)

    await waitFor(() => {
      expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
    })
  })

  test('renders 404 if no program found', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
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
      expect(screen.getByText('beginner, intermediate')).toBeInTheDocument()
    })
  })
})
