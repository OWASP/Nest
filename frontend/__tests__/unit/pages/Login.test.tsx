import { addToast } from '@heroui/toast'
import { screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { useSession, signIn } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import LoginPage from 'app/auth/login/page'

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
jest.mock('utils/credentials', () => ({
  IS_AUTH_ENABLED: true,
}))
describe('LoginPage', () => {
  const pushMock = jest.fn()
  const OLD_ENV = process.env

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({ push: pushMock })
    jest.resetModules()
    process.env = { ...OLD_ENV }
  })

  afterEach(() => {
    process.env = OLD_ENV
  })

  test('renders loading state', () => {
    ;(useSession as jest.Mock).mockReturnValue({ status: 'loading' })
    process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET = 'mock-secret'
    process.env.NEXT_SERVER_GITHUB_CLIENT_ID = 'mock-id'

    render(<LoginPage />)
    expect(screen.getByText(/Checking session/i)).toBeInTheDocument()
  })

  test('shows redirect spinner if authenticated and calls router.push and addToast', () => {
    ;(useSession as jest.Mock).mockReturnValue({ status: 'authenticated' })
    process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET = 'mock-secret'
    process.env.NEXT_SERVER_GITHUB_CLIENT_ID = 'mock-id'

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

  test('shows login button if unauthenticated', () => {
    ;(useSession as jest.Mock).mockReturnValue({ status: 'unauthenticated' })
    process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET = 'mock-secret'
    process.env.NEXT_SERVER_GITHUB_CLIENT_ID = 'mock-id'
    render(<LoginPage />)

    expect(screen.getByText(/Sign in with GitHub/i)).toBeInTheDocument()
  })

  test('calls signIn on GitHub login button click', () => {
    process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET = 'mock-secret'
    process.env.NEXT_SERVER_GITHUB_CLIENT_ID = 'mock-id'
    ;(useSession as jest.Mock).mockReturnValue({ status: 'unauthenticated' })

    render(<LoginPage />)

    fireEvent.click(screen.getByText(/Sign in with GitHub/i))
    expect(signIn).toHaveBeenCalledWith('github', { callbackUrl: '/' })
  })
})

test('does not show login button if GitHub credentials are missing', () => {
  ; (useSession as jest.Mock).mockReturnValue({ status: 'unauthenticated' })
  render(<LoginPage />)

  expect(screen.queryByText(/Sign in with GitHub/i)).not.toBeInTheDocument()
})
