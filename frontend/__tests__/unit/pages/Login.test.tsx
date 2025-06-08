import { addToast } from '@heroui/toast'
import { screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { useSession, signIn } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import LoginPage from 'app/login/page'
import { isAuthEnable } from 'utils/constants'

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
  signIn: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('utils/constants', () => ({
  isAuthEnable: jest.fn(),
  userAuthStatus: {
    LOADING: 'loading',
    AUTHENTICATED: 'authenticated',
    UNAUTHENTICATED: 'unauthenticated',
  },
}))

describe('LoginPage', () => {
  const pushMock = jest.fn()
  const mockIsAuthEnable = isAuthEnable as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({ push: pushMock })
  })

  it('shows "Authentication is disabled" if auth is turned off', () => {
    mockIsAuthEnable.mockReturnValue(false)
    ;(useSession as jest.Mock).mockReturnValue({ status: 'unauthenticated' })

    render(<LoginPage />)

    expect(screen.getByText(/Authentication is disabled/i)).toBeInTheDocument()
  })

  it('renders loading spinner when session is loading', () => {
    mockIsAuthEnable.mockReturnValue(true)
    ;(useSession as jest.Mock).mockReturnValue({ status: 'loading' })

    render(<LoginPage />)

    expect(screen.getByText(/Checking session/i)).toBeInTheDocument()
  })

  it('renders redirect spinner and calls router + toast when authenticated', () => {
    mockIsAuthEnable.mockReturnValue(true)
    ;(useSession as jest.Mock).mockReturnValue({ status: 'authenticated' })

    render(<LoginPage />)

    expect(screen.getByText(/Redirecting/i)).toBeInTheDocument()
    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Already logged in',
        description: 'You are already logged in.',
      })
    )
    expect(pushMock).toHaveBeenCalledWith('/')
  })

  it('shows login button when unauthenticated and auth enabled', () => {
    mockIsAuthEnable.mockReturnValue(true)
    ;(useSession as jest.Mock).mockReturnValue({ status: 'unauthenticated' })

    render(<LoginPage />)

    expect(screen.getByText(/Sign in with GitHub/i)).toBeInTheDocument()
  })

  it('triggers signIn when login button clicked', () => {
    mockIsAuthEnable.mockReturnValue(true)
    ;(useSession as jest.Mock).mockReturnValue({ status: 'unauthenticated' })

    render(<LoginPage />)
    fireEvent.click(screen.getByText(/Sign in with GitHub/i))

    expect(signIn).toHaveBeenCalledWith('github', { callbackUrl: '/' })
  })
})
