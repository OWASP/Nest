import { useQuery } from '@apollo/client/react'
import { mockModuleData } from '@mockData/mockModuleData'
import { screen, waitFor } from '@testing-library/react'
import { useParams } from 'next/navigation'
import React from 'react'
import { render } from 'wrappers/testUtil'
import { handleAppError } from 'app/global-error'
import ModuleDetailsPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
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

jest.mock('components/CardDetailsPage/CardDetailsHeader', () => {
  return function MockHeader(props: { title: string }) {
    return <div data-testid="header">{props.title}</div>
  }
})

jest.mock('components/CardDetailsPage/CardDetailsSummary', () => {
  return function MockSummary(props: { summary: string }) {
    return <div data-testid="summary">{props.summary}</div>
  }
})

jest.mock('components/CardDetailsPage/CardDetailsPageWrapper', () => {
  return function MockWrapper({ children }: { children: React.ReactNode }) {
    return <>{children}</>
  }
})

jest.mock('components/CardDetailsPage/CardDetailsMetadata', () => {
  return function MockMetadata() {
    return <div />
  }
})

jest.mock('components/CardDetailsPage/CardDetailsTags', () => {
  return function MockTags() {
    return <div />
  }
})

jest.mock('components/CardDetailsPage/CardDetailsContributors', () => {
  return function MockContributors() {
    return <div />
  }
})

jest.mock('components/CardDetailsPage/CardDetailsIssuesMilestones', () => {
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

  it('renders module details when data is present', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: mockModuleData,
        getProgram: {
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
        getModule: mockModuleData,
        getProgram: {
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
        getModule: { ...mockModuleData, domains: null },
        getProgram: {
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
        getModule: { ...mockModuleData, tags: null },
        getProgram: {
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
        getModule: { ...mockModuleData, mentors: null },
        getProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('renders module without mentees (uses undefined fallback for line 99)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: { ...mockModuleData, mentees: null },
        getProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('renders module without labels (uses undefined fallback)', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: {
        getModule: { ...mockModuleData, labels: null },
        getProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })

  it('shows "Module Not Found" when getModule returns null', async () => {
    mockUseQuery.mockReturnValue({
      loading: false,
      data: { getModule: null, getProgram: { admins } },
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
        getModule: mockModuleData,
        getProgram: { admins },
      },
    })

    render(<ModuleDetailsPage />)

    expect(await screen.findByTestId('header')).toHaveTextContent('Intro to Web')
  })
})
