import { useQuery } from '@apollo/client/react'
import { mockModuleData } from '@mockData/mockModuleData'
import { screen, waitFor } from '@testing-library/react'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import { handleAppError } from 'app/global-error'
import ModuleDetailsPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn().mockReturnValue({
    data: { user: { login: 'test-user', isLeader: true, isMentor: true } },
    status: 'authenticated',
  }),
}))

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
  ErrorDisplay: ({ title }) => <div>{title}</div>,
}))

jest.mock('components/LoadingSpinner', () => () => <div>LoadingSpinner</div>)

jest.mock('components/cards/Header', () => {
  return function MockHeader(props: { title: string }) {
    return <div data-testid="header">{props.title}</div>
  }
})

jest.mock('components/cards/Summary', () => {
  return function MockSummary(props: { summary: string }) {
    return <div data-testid="summary">{props.summary}</div>
  }
})

jest.mock('components/cards/PageWrapper', () => {
  return function MockWrapper({ children }: { children: React.ReactNode }) {
    return <>{children}</>
  }
})

jest.mock('components/cards/Metadata', () => {
  return function MockMetadata() {
    return <div />
  }
})

jest.mock('components/cards/Tags', () => {
  return function MockTags() {
    return <div />
  }
})

jest.mock('components/cards/Contributors', () => {
  return function MockContributors() {
    return <div />
  }
})

jest.mock('components/cards/IssuesMilestones', () => {
  return function MockIssuesMilestones(props: { onLoadMorePullRequests?: () => void }) {
    return (
      <div>
        {props.onLoadMorePullRequests && (
          <button onClick={props.onLoadMorePullRequests}>Show more</button>
        )}
      </div>
    )
  }
})

describe('ModuleDetailsPage', () => {
  const mockUseParams = useParams as jest.Mock
  const mockUseQuery = useQuery as unknown as jest.Mock

  const admins = [{ login: 'admin1' }]

  beforeEach(() => {
    mockUseParams.mockReturnValue({
      programKey: 'program-1',
      moduleKey: 'module-1',
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('shows loading spinner initially', () => {
    mockUseQuery.mockReturnValue({ loading: true })

    const { container } = render(<ModuleDetailsPage />)
    expect(container.innerHTML).toContain('LoadingSpinner')
  })

  it('calls error handler on GraphQL error', async () => {
    const error = new Error('Query failed')
    mockUseQuery.mockReturnValue({ error, loading: false })

    render(<ModuleDetailsPage />)

    await waitFor(() => {
      expect(handleAppError).toHaveBeenCalledWith(error)
    })
  })

  it('shows access denied when GraphQL error has FORBIDDEN extension', async () => {
    const forbiddenError = {
      graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
    }
    mockUseQuery.mockReturnValue({
      loading: false,
      error: forbiddenError,
      data: undefined,
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByText('Access Denied')).toBeInTheDocument()
    expect(handleAppError).not.toHaveBeenCalled()
  })

  it('renders module details when data is present', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: mockModuleData,
        managementProgram: {
          admins,
        },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
    expect(screen.getByTestId('summary')).toHaveTextContent('A beginner friendly module.')
  })

  it('renders module without admins (uses undefined fallback)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: mockModuleData,
        managementProgram: {
          admins: null,
        },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('renders module without domains (uses undefined fallback)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: { ...mockModuleData, domains: null },
        managementProgram: {
          admins,
        },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('renders module without tags (uses undefined fallback)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: { ...mockModuleData, tags: null },
        managementProgram: {
          admins,
        },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('renders module without mentors (uses undefined fallback for lines 79 & 98)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: { ...mockModuleData, mentors: null },
        managementProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('renders module without mentees (uses undefined fallback for line 99)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: { ...mockModuleData, mentees: null },
        managementProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('renders module without labels (uses undefined fallback)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        managementModule: { ...mockModuleData, labels: null },
        managementProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('shows "Module Not Found" when managementModule returns null', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: { managementModule: null, managementProgram: { admins } },
    })

    render(<ModuleDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Module Not Found')).toBeInTheDocument()
    })
  })

  it('shows "Module Not Found" when data is undefined', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: undefined,
    })

    render(<ModuleDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Module Not Found')).toBeInTheDocument()
    })
  })

  it('shows loading spinner when isLoading true and no module cached', () => {
    mockUseQuery.mockReturnValue({ loading: true, data: undefined })

    const { container } = render(<ModuleDetailsPage />)
    expect(container.innerHTML).toContain('LoadingSpinner')
  })

  it('does not show loading spinner when isLoading true but module is already cached', async () => {
    mockUseQuery.mockReturnValue({
      loading: true,
      data: {
        managementModule: mockModuleData,
        managementProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })
  it('renders mentee view when management query returns forbidden error', async () => {
    const { useSession } = jest.requireMock('next-auth/react')
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'mentee1', isLeader: false, isMentor: false } },
      status: 'authenticated',
    })
    const forbiddenError = {
      graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
      message: 'Forbidden',
    }
    const menteeModuleData = {
      getModule: {
        id: '1',
        key: 'owasp-nest',
        name: 'OWASP Nest',
        description: 'Nest module',
        experienceLevel: 'BEGINNER',
        startedAt: '2025-01-01',
        endedAt: '2025-12-31',
        domains: [],
        tags: [],
        labels: [],
        mentors: [],
        mentees: [],
        order: 0,
      },
    }
    mockUseQuery.mockImplementation(
      (query: { definitions?: Array<{ name?: { value?: string } }> }) => {
        const opName = query?.definitions?.[0]?.name?.value ?? ''
        if (opName === 'GetManagementProgramAdminsAndModules') {
          return { data: null, loading: false, error: forbiddenError }
        }
        return { data: menteeModuleData, loading: false, error: undefined }
      }
    )
    render(<ModuleDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })
  })

  it('shows module not found for mentee when getModule returns null', async () => {
    const { useSession } = jest.requireMock('next-auth/react')
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'mentee1', isLeader: false, isMentor: false } },
      status: 'authenticated',
    })
    const forbiddenError = {
      graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
      message: 'Forbidden',
    }
    mockUseQuery.mockImplementation(
      (query: { definitions?: Array<{ name?: { value?: string } }> }) => {
        const opName = query?.definitions?.[0]?.name?.value ?? ''
        if (opName === 'GetManagementProgramAdminsAndModules') {
          return { data: null, loading: false, error: forbiddenError }
        }
        return { data: { getModule: null }, loading: false, error: undefined }
      }
    )
    render(<ModuleDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText(/Module Not Found/i)).toBeInTheDocument()
    })
  })
})

describe('Mentee view', () => {
  const mockUseQueryLocal = useQuery as unknown as jest.Mock
  const forbiddenError = {
    graphQLErrors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }],
    message: 'Forbidden',
  }

  beforeEach(() => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { login: 'mentee1', isLeader: false, isMentor: false } },
      status: 'authenticated',
    })
  })

  it('shows loading spinner while mentee module is loading', () => {
    mockUseQueryLocal.mockImplementation(() => {
      if (
        mockUseQueryLocal.mock.calls[mockUseQueryLocal.mock.calls.length - 1]?.[1]?.skip === false
      ) {
        return { data: undefined, loading: true, error: undefined }
      }
      return { data: null, loading: false, error: forbiddenError }
    })
    mockUseQueryLocal
      .mockReturnValueOnce({ data: null, loading: false, error: forbiddenError })
      .mockReturnValueOnce({ data: undefined, loading: true, error: undefined })
    const { container } = render(<ModuleDetailsPage />)
    expect(container.innerHTML).toContain('LoadingSpinner')
  })

  it('shows module not found when mentee module data is null', async () => {
    mockUseQueryLocal
      .mockReturnValueOnce({ data: null, loading: false, error: forbiddenError })
      .mockReturnValueOnce({ data: { getModule: null }, loading: false, error: undefined })
    render(<ModuleDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Module Not Found')).toBeInTheDocument()
    })
  })

  it('renders mentee module details when data is available', async () => {
    mockUseQueryLocal
      .mockReturnValueOnce({ data: null, loading: false, error: forbiddenError })
      .mockReturnValueOnce({
        data: {
          getModule: {
            ...mockModuleData,
            name: 'Mentee Module',
            description: 'Mentee module description',
            experienceLevel: 'beginner',
            startedAt: '2026-01-01',
            endedAt: '2026-12-01',
            tags: [],
            domains: [],
            mentors: [],
            mentees: [],
          },
        },
        loading: false,
        error: undefined,
      })
    render(<ModuleDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Mentee Module')).toBeInTheDocument()
    })
  })
})
