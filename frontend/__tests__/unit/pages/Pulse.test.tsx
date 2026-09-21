import { useApolloClient, useQuery } from '@apollo/client/react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { useRouter, useSearchParams } from 'next/navigation'
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import PulsePage from 'app/pulse/page'
import {
  GetActivityEventsDocument,
  GetActivityEventStatsDocument,
} from 'types/__generated__/pulseQueries.generated'

const mockRouter = {
  replace: jest.fn(),
}

let mockSearchParams = new URLSearchParams()

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => mockRouter),
  useSearchParams: jest.fn(() => mockSearchParams),
}))

const mockApolloClient = {
  query: jest.fn(),
}

jest.mock('@apollo/client/react', () => ({
  useApolloClient: jest.fn(() => mockApolloClient),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/button', () => {
  const MockButton = ({
    children,
    onPress,
    isIconOnly: _isIconOnly,
    isPressable: _isPressable,
    variant: _variant,
    radius: _radius,
    size: _size,
    color: _color,
    fullWidth: _fullWidth,
    isDisabled: _isDisabled,
    isLoading: _isLoading,
    disableRipple: _disableRipple,
    disableAnimation: _disableAnimation,
    ...props
  }: {
    children: ReactNode
    onPress?: () => void
    [key: string]: unknown
  }) => (
    <button onClick={onPress} {...(props as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  )
  MockButton.displayName = 'MockButton'
  return {
    __esModule: true,
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Button: MockButton,
  }
})

jest.mock('components/Pagination', () => ({
  __esModule: true,
  default: ({
    currentPage,
    onPageChange,
  }: {
    currentPage: number
    onPageChange: (page: number) => void
  }) => (
    <div data-testid="pagination">
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ),
}))

const mockStatsData = {
  activityEventStats: {
    __typename: 'ActivityEventStatsNode' as const,
    totalActivities: 1200,
    pullRequests: 300,
    issues: 450,
    contributors: 75,
    releases: 20,
    activeRepos: 15,
  },
}

const mockEventsData = {
  activityEvents: {
    __typename: 'PaginatedActivityEvents',
    currentPage: 1,
    totalPages: 3,
    totalCount: 45,
    events: [
      {
        __typename: 'ActivityEventNode' as const,
        id: 'evt-today',
        activityType: 'pr_opened',
        occurredAt: new Date().toISOString(),
        title: 'Fix issue with login',
        url: 'https://github.com/owasp/nest/pull/101',
        number: 101,
        githubUser: {
          __typename: 'UserNode' as const,
          id: 'u-1',
          login: 'john_doe',
          name: 'John Doe',
          avatarUrl: 'https://example.com/john.png',
        },
        githubRepository: {
          __typename: 'RepositoryNode' as const,
          id: 'r-1',
          key: 'nest',
          name: 'nest',
          url: 'https://github.com/owasp/nest',
        },
      },
      {
        __typename: 'ActivityEventNode' as const,
        id: 'evt-yesterday',
        activityType: 'issue_opened',
        occurredAt: new Date(Date.now() - 86400000).toISOString(),
        title: 'Add dark mode toggle',
        url: 'https://github.com/owasp/nest/issues/102',
        number: 102,
        githubUser: {
          __typename: 'UserNode' as const,
          id: 'u-2',
          login: 'jane_smith',
          name: 'Jane Smith',
          avatarUrl: 'https://example.com/jane.png',
        },
        githubRepository: {
          __typename: 'RepositoryNode' as const,
          id: 'r-1',
          key: 'nest',
          name: 'nest',
          url: 'https://github.com/owasp/nest',
        },
      },
      {
        __typename: 'ActivityEventNode' as const,
        id: 'evt-older',
        activityType: 'release_published',
        occurredAt: new Date('2024-01-15T12:00:00Z').toISOString(),
        title: 'Version 2.0 Released',
        url: 'https://github.com/owasp/nest/releases/tag/v2.0',
        number: null,
        githubUser: null,
        githubRepository: {
          __typename: 'RepositoryNode' as const,
          id: 'r-1',
          key: 'nest',
          name: 'nest',
          url: 'https://github.com/owasp/nest',
        },
      },
    ],
  },
}

describe('<PulsePage />', () => {
  beforeEach(() => {
    mockSearchParams = new URLSearchParams()
    jest.clearAllMocks()
    ;(useRouter as unknown as jest.Mock).mockReturnValue(mockRouter)
    ;(useSearchParams as unknown as jest.Mock).mockImplementation(() => mockSearchParams)
    ;(useApolloClient as unknown as jest.Mock).mockReturnValue(mockApolloClient)
    ;(useQuery as unknown as jest.Mock).mockImplementation((doc) => {
      if (doc === GetActivityEventStatsDocument) {
        return { data: mockStatsData, loading: false, error: null }
      }
      if (doc === GetActivityEventsDocument) {
        return { data: mockEventsData, loading: false, error: null }
      }
      return { data: null, loading: false, error: null }
    })
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('handles query states, date formatting fallback, and invalid URL parameters', () => {
    mockSearchParams = new URLSearchParams('page=invalid_number&order=unknown_order')
    const dateSpy = jest.spyOn(Date.prototype, 'toLocaleDateString').mockImplementation(() => {
      throw new Error('Date crash')
    })

    const { rerender } = render(<PulsePage />)
    expect(screen.getByText('ACTIVITY STREAM')).toBeInTheDocument()
    dateSpy.mockRestore()

    ;(useQuery as unknown as jest.Mock).mockImplementation((doc) => {
      if (doc === GetActivityEventStatsDocument) return { data: mockStatsData, loading: false }
      if (doc === GetActivityEventsDocument) return { data: null, loading: true }
      return { data: null, loading: false }
    })
    rerender(<PulsePage />)
    expect(screen.getByText('Loading OWASP activity stream...')).toBeInTheDocument()

    ;(useQuery as unknown as jest.Mock).mockImplementation((doc) => {
      if (doc === GetActivityEventStatsDocument)
        return { data: null, loading: false, error: new Error('Stats err') }
      if (doc === GetActivityEventsDocument)
        return { data: null, loading: false, error: new Error('Failed to fetch events') }
      return { data: null, loading: false }
    })
    rerender(<PulsePage />)
    expect(screen.getByText('GraphQL Query Error')).toBeInTheDocument()

    ;(useQuery as unknown as jest.Mock).mockImplementation((doc) => {
      if (doc === GetActivityEventStatsDocument) return { data: mockStatsData, loading: false }
      if (doc === GetActivityEventsDocument) {
        return {
          data: { activityEvents: { currentPage: 1, totalPages: 1, totalCount: 0, events: [] } },
          loading: false,
        }
      }
      return { data: null, loading: false }
    })
    rerender(<PulsePage />)
    expect(screen.getByText('No activities found')).toBeInTheDocument()

    ;(useQuery as unknown as jest.Mock).mockImplementation(() => ({
      data: undefined,
      loading: false,
    }))
    rerender(<PulsePage />)
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('initializes filters from URL, handles search, clear all, and pagination', async () => {
    jest.useFakeTimers()
    mockSearchParams = new URLSearchParams(
      'activityType=pr_opened&project=nest&chapter=london&order=asc&timeRange=7d&search=john'
    )

    const { rerender } = render(<PulsePage />)
    expect(screen.getByText('Active filters:')).toBeInTheDocument()

    mockSearchParams = new URLSearchParams(
      'activityType=pr_opened&project=nest&chapter=london&order=asc&timeRange=7d&search=john'
    )
    rerender(<PulsePage />)

    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    expect(mockRouter.replace).toHaveBeenCalledWith(
      '?activityType=pr_opened&project=nest&chapter=london&timeRange=7d&order=asc&search=john'
    )

    mockSearchParams = new URLSearchParams(
      'activityType=pr_opened&project=nest&chapter=london&search=john'
    )
    rerender(<PulsePage />)

    fireEvent.click(screen.getByText('Clear all'))
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    expect(mockRouter.replace).toHaveBeenCalledWith('?')

    const searchInput = screen.getByRole('textbox', { name: 'Search activity' })
    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'owasp' } })
      jest.runAllTimers()
    })
    expect(mockRouter.replace).toHaveBeenCalledWith('?search=owasp')

    fireEvent.click(screen.getByText('Next Page'))
    expect(mockRouter.replace).toHaveBeenCalledWith('?search=owasp&page=2')
  })

  it('fetches and selects project and chapter suggestions including empty names', async () => {
    jest.useFakeTimers()
    mockApolloClient.query
      .mockResolvedValueOnce({
        data: { searchProjects: [{ id: 'p1', name: 'OWASP Nest' }] },
      })
      .mockResolvedValueOnce({
        data: { searchProjects: [{ id: 'p2', name: '' }] },
      })
      .mockResolvedValueOnce({
        data: { searchChapters: [{ id: 'c1', name: 'OWASP London' }] },
      })
      .mockResolvedValueOnce({
        data: { searchChapters: [{ id: 'c2', name: '' }] },
      })

    render(<PulsePage />)

    const projectInput = screen.getByRole('textbox', { name: 'Filter by project' })
    fireEvent.focus(projectInput)
    fireEvent.change(projectInput, { target: { value: 'nest' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => {
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText('OWASP Nest'))
    expect(projectInput).toHaveValue('OWASP Nest')

    fireEvent.change(projectInput, { target: { value: 'empty' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => {
      const items = screen.getAllByRole('button')
      const emptyBtn = items.find((btn) => btn.textContent === '')
      if (emptyBtn) fireEvent.click(emptyBtn)
    })

    const chapterInput = screen.getByRole('textbox', { name: 'Filter by chapter' })
    fireEvent.focus(chapterInput)
    fireEvent.change(chapterInput, { target: { value: 'london' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => {
      expect(screen.getByText('OWASP London')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText('OWASP London'))
    expect(chapterInput).toHaveValue('OWASP London')

    fireEvent.change(chapterInput, { target: { value: 'empty' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => {
      const items = screen.getAllByRole('button')
      const emptyBtn = items.find((btn) => btn.textContent === '')
      if (emptyBtn) fireEvent.click(emptyBtn)
    })
  })

  it('handles suggestion fetch errors, null responses, and stale queries', async () => {
    jest.useFakeTimers()
    mockApolloClient.query
      .mockRejectedValueOnce(new Error('Project fetch failed'))
      .mockResolvedValueOnce({ data: { searchProjects: null } })
      .mockRejectedValueOnce(new Error('Chapter fetch failed'))
      .mockResolvedValueOnce({ data: { searchChapters: null } })

    render(<PulsePage />)

    const projectInput = screen.getByRole('textbox', { name: 'Filter by project' })
    fireEvent.focus(projectInput)
    fireEvent.change(projectInput, { target: { value: 'nest' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => {
      expect(screen.getByText('No project suggestions found')).toBeInTheDocument()
    })

    fireEvent.change(projectInput, { target: { value: 'nest2' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })

    const chapterInput = screen.getByRole('textbox', { name: 'Filter by chapter' })
    fireEvent.focus(chapterInput)
    fireEvent.change(chapterInput, { target: { value: 'london' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => {
      expect(screen.getByText('No chapter suggestions found')).toBeInTheDocument()
    })

    fireEvent.change(chapterInput, { target: { value: 'london2' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })

    let resolveP1: (val: unknown) => void
    let rejectP2: (err: Error) => void
    const p1 = new Promise((res) => {
      resolveP1 = res
    })
    const p2 = new Promise((_, rej) => {
      rejectP2 = rej
    })

    mockApolloClient.query.mockImplementationOnce(() => p1)
    fireEvent.change(projectInput, { target: { value: 'p1' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })

    mockApolloClient.query.mockImplementationOnce(() => p2)
    fireEvent.change(projectInput, { target: { value: 'p2' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })

    await act(async () => {
      resolveP1({ data: { searchProjects: [{ id: 'p1', name: 'Stale P1' }] } })
      rejectP2(new Error('Stale P2 err'))
    })

    let rejectC1: (err: Error) => void
    let resolveC2: (val: unknown) => void
    const c1 = new Promise((_, rej) => {
      rejectC1 = rej
    })
    const c2 = new Promise((res) => {
      resolveC2 = res
    })

    mockApolloClient.query.mockImplementationOnce(() => c1)
    fireEvent.focus(chapterInput)
    fireEvent.change(chapterInput, { target: { value: 'c1' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })

    mockApolloClient.query.mockImplementationOnce(() => c2)
    fireEvent.change(chapterInput, { target: { value: 'c2' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })

    await act(async () => {
      rejectC1(new Error('Stale C1 err'))
      resolveC2({ data: { searchChapters: [{ id: 'c2', name: 'Stale C2' }] } })
    })

    mockApolloClient.query.mockResolvedValueOnce({
      data: { searchChapters: [{ id: 'c3', name: 'Fresh Chapter' }] },
    })
    fireEvent.change(chapterInput, { target: { value: 'c3' } })
    await act(async () => {
      jest.advanceTimersByTime(350)
    })
    await waitFor(() => {
      expect(screen.getByText('Fresh Chapter')).toBeInTheDocument()
    })
  })
})
