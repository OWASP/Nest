import { useQuery } from '@apollo/client'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { useRouter as useRouterMock } from 'next/navigation'
import { useSession as mockUseSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import MyMentorshipPage from 'app/my/mentorship/page'

jest.mock('@apollo/client', () => {
  const actual = jest.requireActual('@apollo/client')
  return {
    ...actual,
    useQuery: jest.fn(),
  }
})

jest.mock('next/navigation', () => {
  const actual = jest.requireActual('next/navigation')
  return {
    ...actual,
    useRouter: jest.fn(),
    useSearchParams: () => new URLSearchParams(''),
  }
})

jest.mock('next-auth/react', () => {
  const actual = jest.requireActual('next-auth/react')
  return {
    ...actual,
    useSession: jest.fn(),
  }
})
jest.mock('hooks/useUpdateProgramStatus', () => ({
  useUpdateProgramStatus: () => ({ updateProgramStatus: jest.fn() }),
}))

const mockUseQuery = useQuery as jest.Mock
const mockPush = jest.fn()

beforeEach(() => {
  jest.clearAllMocks()
  ;(useRouterMock as jest.Mock).mockReturnValue({ push: mockPush })
})

const mockProgramData = {
  myPrograms: {
    programs: [
      {
        id: '1',
        key: 'program-1',
        name: 'Test Program',
        description: 'Test Description',
        status: 'draft',
        startedAt: '2025-07-28',
        endedAt: '2025-08-10',
        experienceLevels: ['beginner'],
        menteesLimit: 10,
        admins: [],
      },
    ],
    totalPages: 1,
  },
}

describe('MyMentorshipPage', () => {
  it('shows loading while checking access', () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'loading',
    })
    mockUseQuery.mockReturnValue({ data: undefined, loading: false, error: undefined })

    render(<MyMentorshipPage />)
    expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
  })

  it('shows access denied if user is not project leader', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'user 1',
          email: 'user@example.com',
          login: 'user1',
          isLeader: false,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
    })

    mockUseQuery.mockReturnValue({ data: undefined, loading: false, error: undefined })

    render(<MyMentorshipPage />)
    expect(await screen.findByText(/Access Denied/i)).toBeInTheDocument()
  })

  it('renders mentorship programs if user is leader', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'User',
          email: 'leader@example.com',
          login: 'user',
          isLeader: true,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
    })

    mockUseQuery.mockReturnValue({
      data: mockProgramData,
      loading: false,
      error: undefined,
    })

    render(<MyMentorshipPage />)
    expect(await screen.findByText('My Mentorship')).toBeInTheDocument()
    expect(await screen.findByText('Test Program')).toBeInTheDocument()
  })

  it('shows empty state when no programs found', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'User',
          email: 'user@example.com',
          login: 'user',
          isLeader: true,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
    })

    mockUseQuery.mockReturnValue({
      data: { myPrograms: { programs: [], totalPages: 1 } },
      loading: false,
      error: undefined,
    })

    render(<MyMentorshipPage />)
    expect(await screen.findByText(/Program not found/i)).toBeInTheDocument()
  })

  it('navigates to create page on clicking create button', async () => {
    ;(mockUseSession as jest.Mock).mockReturnValue({
      data: {
        user: {
          name: 'User',
          email: 'user@example.com',
          login: 'User',
          isLeader: true,
        },
        expires: '2099-01-01T00:00:00.000Z',
      },
      status: 'authenticated',
    })

    mockUseQuery.mockReturnValue({
      data: mockProgramData,
      loading: false,
      error: undefined,
    })

    render(<MyMentorshipPage />)

    const btn = await screen.findByRole('button', { name: /create program/i })
    fireEvent.click(btn)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/create')
    })
  })
})
