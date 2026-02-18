import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { useRouter as useRouterMock } from 'next/navigation'
import { useSession as mockUseSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import MyMentorshipPage from 'app/my/mentorship/page'

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('@apollo/client/react', () => {
  const actual = jest.requireActual('@apollo/client/react')
  return {
    ...actual,
    useQuery: jest.fn(),
  }
})

jest.mock('components/SearchPageLayout', () => {
  return function MockSearchPageLayout({
    onSearch,
    onPageChange,
    children,
  }: {
    onSearch?: (q: string) => void
    onPageChange?: (page: number) => void
    children: React.ReactNode
    [key: string]: unknown
  }) {
    return (
      <div data-testid="search-page-layout">
        {children}
        <input
          data-testid="search-input"
          type="text"
          onChange={(e) => onSearch?.(e.target.value)}
          placeholder="Search"
        />
        <button data-testid="next-page-btn" onClick={() => onPageChange?.(2)}>
          Next Page
        </button>
      </div>
    )
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

const mockUseQuery = useQuery as unknown as jest.Mock
const mockPush = jest.fn()
const mockAddToast = addToast as jest.Mock

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

  it('shows an error toast when GraphQL query fails', async () => {
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
      data: undefined,
      loading: false,
      error: new Error('GraphQL error'),
    })

    render(<MyMentorshipPage />)

    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'GraphQL Error',
          description: 'Failed to fetch your programs',
          color: 'danger',
        })
      )
    })
  })

  it('handles page change callback', async () => {
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
      data: mockProgramData,
      loading: false,
      error: undefined,
    })

    const scrollToMock = jest.fn()
    const originalScrollTo = globalThis.scrollTo
    globalThis.scrollTo = scrollToMock

    try {
      render(<MyMentorshipPage />)

      await waitFor(() => {
        expect(screen.getByText('My Mentorship')).toBeInTheDocument()
      })

      const nextPageBtn = screen.getByTestId('next-page-btn')
      fireEvent.click(nextPageBtn)

      await waitFor(() => {
        expect(scrollToMock).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })
      })
    } finally {
      // Restore original scrollTo to avoid leaking mock into other tests
      globalThis.scrollTo = originalScrollTo
    }
  })

  it('updates URL when search or page changes', async () => {
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
      data: mockProgramData,
      loading: false,
      error: undefined,
    })

    render(<MyMentorshipPage />)

    await waitFor(() => {
      expect(screen.getByText('My Mentorship')).toBeInTheDocument()
    })

    const searchInput = screen.getByTestId('search-input')
    fireEvent.change(searchInput, { target: { value: 'query' } })

    await waitFor(
      () => {
        expect(mockPush).toHaveBeenCalledWith('?q=query', { scroll: false })
      },
      { timeout: 1000 }
    )
  })

  it('handles missing totalPages in program data', async () => {
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
      data: {
        myPrograms: {
          programs: mockProgramData.myPrograms.programs,
          totalPages: null, // Test fallback
        },
      },
      loading: false,
      error: undefined,
    })

    render(<MyMentorshipPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })
  })

  it('cleans up debounce on unmount', () => {
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
      data: mockProgramData,
      loading: false,
      error: undefined,
    })

    const { unmount } = render(<MyMentorshipPage />)
    expect(screen.getByText('My Mentorship')).toBeInTheDocument()
    unmount()
  })

  it('updates debounced search query', async () => {
    jest.useFakeTimers()
    try {
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
        data: mockProgramData,
        loading: false,
        error: undefined,
      })

      render(<MyMentorshipPage />)

      const searchInput = screen.getByTestId('search-input')
      fireEvent.change(searchInput, { target: { value: 'debounced' } })

      React.act(() => {
        jest.advanceTimersByTime(500)
      })

      await waitFor(() => {
        expect(mockUseQuery).toHaveBeenCalledWith(
          expect.anything(),
          expect.objectContaining({
            variables: expect.objectContaining({ search: 'debounced' }),
          })
        )
      })
    } finally {
      jest.useRealTimers()
    }
  })
})
