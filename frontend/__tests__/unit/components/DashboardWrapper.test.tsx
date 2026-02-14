import { render, screen } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { notFound } from 'next/navigation'
import DashboardWrapper from 'components/DashboardWrapper'

jest.mock('hooks/useDjangoSession')

jest.mock('next/navigation', () => ({
  notFound: jest.fn(() => {
    throw new Error('notFound')
  }),
}))

jest.mock('components/LoadingSpinner', () => {
  return function MockLoadingSpinner() {
    return <div data-testid="loading-spinner">Loading...</div>
  }
})

describe('<DashboardWrapper />', () => {
  const mockUseDjangoSession = useDjangoSession as jest.MockedFunction<typeof useDjangoSession>
  const mockNotFound = notFound as jest.MockedFunction<typeof notFound>

  const mockSession = {
    user: {
      id: '1',
      name: 'Test User',
      email: 'test@example.com',
      image: 'https://example.com/image.jpg',
      isOwaspStaff: true,
    },
    accessToken: 'test-token',
    expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders LoadingSpinner when isSyncing is true', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: true,
      session: mockSession,
      status: 'authenticated',
    })

    render(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    expect(screen.queryByText('Dashboard Content')).not.toBeInTheDocument()
  })

  it('renders children when isSyncing is false and user is OWASP staff', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: mockSession,
      status: 'authenticated',
    })

    render(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
    expect(screen.getByText('Dashboard Content')).toBeInTheDocument()
    expect(mockNotFound).not.toHaveBeenCalled()
  })

  it('calls notFound when user is not OWASP staff', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: {
        ...mockSession,
        user: {
          ...mockSession.user,
          isOwaspStaff: false,
        },
      },
      status: 'authenticated',
    })

    expect(() => {
      render(
        <DashboardWrapper>
          <div>Dashboard Content</div>
        </DashboardWrapper>
      )
    }).toThrow('notFound')
    expect(mockNotFound).toHaveBeenCalled()
  })

  it('calls notFound when session is undefined', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: undefined,
      status: 'unauthenticated',
    })

    expect(() => {
      render(
        <DashboardWrapper>
          <div>Dashboard Content</div>
        </DashboardWrapper>
      )
    }).toThrow('notFound')
    expect(mockNotFound).toHaveBeenCalled()
  })

  it('prioritizes loading state over authorization check', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: true,
      session: {
        ...mockSession,
        user: {
          ...mockSession.user,
          isOwaspStaff: false,
        },
      },
      status: 'authenticated',
    })

    render(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    expect(mockNotFound).not.toHaveBeenCalled()
  })

  it('handles status transitions correctly', () => {
    // Initially syncing
    mockUseDjangoSession.mockReturnValue({
      isSyncing: true,
      session: mockSession,
      status: 'loading',
    })

    const { rerender } = render(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    rerender(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

    // After sync completes
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: mockSession,
      status: 'authenticated',
    })

    rerender(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
    expect(screen.getByText('Dashboard Content')).toBeInTheDocument()
  })

  it('handles authorization changes when session is updated', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: mockSession,
      status: 'authenticated',
    })

    const { rerender } = render(
      <DashboardWrapper>
        <div>Dashboard Content</div>
      </DashboardWrapper>
    )

    expect(screen.getByText('Dashboard Content')).toBeInTheDocument()
    mockNotFound.mockClear()

    // Update to non-staff user
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: {
        ...mockSession,
        user: {
          ...mockSession.user,
          isOwaspStaff: false,
        },
      },
      status: 'authenticated',
    })

    expect(() => {
      rerender(
        <DashboardWrapper>
          <div>Dashboard Content</div>
        </DashboardWrapper>
      )
    }).toThrow('notFound')

    expect(mockNotFound).toHaveBeenCalled()
  })

  it('renders children without extra wrapper', () => {
    mockUseDjangoSession.mockReturnValue({
      isSyncing: false,
      session: mockSession,
      status: 'authenticated',
    })

    const { container } = render(
      <DashboardWrapper>
        <div>Test 1</div>
        <div>Test 2</div>
      </DashboardWrapper>
    )

    expect(screen.getByText('Test 1')).toBeInTheDocument()
    expect(screen.getByText('Test 2')).toBeInTheDocument()

    const divElements = container.querySelectorAll('div')
    const testDivs = Array.from(divElements).filter(
      (div) => div.textContent === 'Test 1' || div.textContent === 'Test 2'
    )
    expect(testDivs.length).toBe(2)
  })
})
