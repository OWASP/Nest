import { addToast } from '@heroui/toast'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import type { Session } from 'next-auth'
import { useSession, signIn } from 'next-auth/react'
import { userAuthStatus } from 'utils/constants'
import LoginPageContent from 'components/LoginPageContent'

// Define types for mock props
interface MockFontAwesomeIconProps {
  icon: {
    iconName?: string
  }
  spin?: boolean
  height?: number
  width?: number
}

interface MockRouterReturn {
  push: jest.MockedFunction<(url: string) => void>
  replace: jest.MockedFunction<(url: string) => void>
  back: jest.MockedFunction<() => void>
  forward: jest.MockedFunction<() => void>
  refresh: jest.MockedFunction<() => void>
  prefetch: jest.MockedFunction<(url: string) => void>
}

// Mock dependencies
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

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, spin, ...props }: MockFontAwesomeIconProps) => (
    <span
      data-testid="font-awesome-icon"
      data-icon={icon.iconName || 'unknown'}
      data-spin={spin}
      {...props}
    >
      {icon.iconName || 'icon'}
    </span>
  ),
}))

describe('LoginPageContent', () => {
  const mockPush = jest.fn()
  const mockUseSession = useSession as jest.MockedFunction<typeof useSession>
  const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>
  const mockSignIn = signIn as jest.MockedFunction<typeof signIn>
  const mockAddToast = addToast as jest.MockedFunction<typeof addToast>

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({
      push: mockPush,
      replace: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      prefetch: jest.fn(),
    } as MockRouterReturn)
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders with GitHub authentication enabled', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Welcome back')).toBeInTheDocument()
      expect(screen.getByText('Sign in with your GitHub account to continue')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in with github/i })).toBeInTheDocument()
    })

    it('renders with GitHub authentication disabled', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={false} />)

      expect(screen.getByText('Signing In with GitHub is not enabled.')).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: /sign in with github/i })).not.toBeInTheDocument()
    })
  })

  describe('Conditional rendering logic', () => {
    it('shows loading state when session status is loading', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.LOADING as 'loading',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Checking session...')).toBeInTheDocument()
      expect(screen.getByTestId('font-awesome-icon')).toHaveAttribute('data-icon', 'spinner')
      expect(screen.getByTestId('font-awesome-icon')).toHaveAttribute('data-spin', 'true')
    })

    it('shows redirecting state when user is authenticated', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.AUTHENTICATED as 'authenticated',
        data: { user: { name: 'Test User', email: 'test@example.com' } } as Session,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Redirecting...')).toBeInTheDocument()
      expect(screen.getByTestId('font-awesome-icon')).toHaveAttribute('data-icon', 'spinner')
      expect(screen.getByTestId('font-awesome-icon')).toHaveAttribute('data-spin', 'true')
    })

    it('shows login form when user is unauthenticated and GitHub auth is enabled', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Welcome back')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in with github/i })).toBeInTheDocument()
      expect(screen.getByTestId('font-awesome-icon')).toHaveAttribute('data-icon', 'github')
    })

    it('shows disabled message when GitHub auth is disabled regardless of session status', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={false} />)

      expect(screen.getByText('Signing In with GitHub is not enabled.')).toBeInTheDocument()
      expect(screen.queryByText('Welcome back')).not.toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('correctly handles isGitHubAuthEnabled prop when true', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByRole('button', { name: /sign in with github/i })).toBeInTheDocument()
      expect(screen.queryByText('Signing In with GitHub is not enabled.')).not.toBeInTheDocument()
    })

    it('correctly handles isGitHubAuthEnabled prop when false', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={false} />)

      expect(screen.queryByRole('button', { name: /sign in with github/i })).not.toBeInTheDocument()
      expect(screen.getByText('Signing In with GitHub is not enabled.')).toBeInTheDocument()
    })
  })

  describe('Event handling', () => {
    it('calls signIn with correct parameters when GitHub sign-in button is clicked', async () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      const signInButton = screen.getByRole('button', { name: /sign in with github/i })
      fireEvent.click(signInButton)

      expect(mockSignIn).toHaveBeenCalledWith('github', { callbackUrl: '/' })
    })

    it('does not call signIn when GitHub auth is disabled', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={false} />)

      expect(screen.queryByRole('button', { name: /sign in with github/i })).not.toBeInTheDocument()
      expect(mockSignIn).not.toHaveBeenCalled()
    })
  })

  describe('State changes / internal logic', () => {
    it('redirects and shows toast when user becomes authenticated', async () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.AUTHENTICATED as 'authenticated',
        data: { user: { name: 'Test User', email: 'test@example.com' } } as Session,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      await waitFor(() => {
        expect(mockAddToast).toHaveBeenCalledWith({
          description: 'You are already logged in.',
          title: 'Already logged in',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
          color: 'default',
          variant: 'solid',
        })
      })

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/')
      })
    })

    it('handles session status changes correctly', () => {
      const { rerender } = render(<LoginPageContent isGitHubAuthEnabled={true} />)

      // Initially loading
      mockUseSession.mockReturnValue({
        status: userAuthStatus.LOADING as 'loading',
        data: null,
        update: jest.fn(),
      })
      rerender(<LoginPageContent isGitHubAuthEnabled={true} />)
      expect(screen.getByText('Checking session...')).toBeInTheDocument()

      // Then unauthenticated
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })
      rerender(<LoginPageContent isGitHubAuthEnabled={true} />)
      expect(screen.getByText('Welcome back')).toBeInTheDocument()
    })
  })

  describe('Default values and fallbacks', () => {
    it('renders correctly when session data is null', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Welcome back')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in with github/i })).toBeInTheDocument()
    })

    it('handles undefined session status gracefully', () => {
      mockUseSession.mockReturnValue({
        status: 'unknown' as 'authenticated' | 'unauthenticated' | 'loading',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      // Should render the login form as fallback
      expect(screen.getByText('Welcome back')).toBeInTheDocument()
    })
  })

  describe('Text and content rendering', () => {
    it('renders all text content correctly for login form', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Welcome back')).toBeInTheDocument()
      expect(screen.getByText('Sign in with your GitHub account to continue')).toBeInTheDocument()
      expect(screen.getByText('Sign In with GitHub')).toBeInTheDocument()
    })

    it('renders loading state text correctly', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.LOADING as 'loading',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Checking session...')).toBeInTheDocument()
    })

    it('renders redirecting state text correctly', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.AUTHENTICATED as 'authenticated',
        data: { user: { name: 'Test User' } } as Session,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      expect(screen.getByText('Redirecting...')).toBeInTheDocument()
    })

    it('renders disabled state text correctly', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={false} />)

      expect(screen.getByText('Signing In with GitHub is not enabled.')).toBeInTheDocument()
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles boolean props correctly', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      // Test with explicit false
      const { rerender } = render(<LoginPageContent isGitHubAuthEnabled={false} />)
      expect(screen.getByText('Signing In with GitHub is not enabled.')).toBeInTheDocument()

      // Test with explicit true
      rerender(<LoginPageContent isGitHubAuthEnabled={true} />)
      expect(screen.getByText('Welcome back')).toBeInTheDocument()
    })

    it('calls router.push when user is authenticated', async () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.AUTHENTICATED as 'authenticated',
        data: { user: { name: 'Test User' } } as Session,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      // Wait for the useEffect to trigger the redirect
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/')
      })

      expect(screen.getByText('Redirecting...')).toBeInTheDocument()
    })
  })

  describe('Accessibility roles and labels', () => {
    it('has proper heading structure', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      const heading = screen.getByRole('heading', { level: 2 })
      expect(heading).toHaveTextContent('Welcome back')
    })

    it('has accessible button for sign in', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      const button = screen.getByRole('button', { name: /sign in with github/i })
      expect(button).toBeInTheDocument()
      // Button doesn't have explicit type attribute, defaults to submit for form buttons
      expect(button).not.toHaveAttribute('type')
    })

    it('provides meaningful text for screen readers in all states', () => {
      // Test loading state
      mockUseSession.mockReturnValue({
        status: userAuthStatus.LOADING as 'loading',
        data: null,
        update: jest.fn(),
      })

      const { rerender } = render(<LoginPageContent isGitHubAuthEnabled={true} />)
      expect(screen.getByText('Checking session...')).toBeInTheDocument()

      // Test redirecting state
      mockUseSession.mockReturnValue({
        status: userAuthStatus.AUTHENTICATED as 'authenticated',
        data: { user: { name: 'Test User' } } as Session,
        update: jest.fn(),
      })
      rerender(<LoginPageContent isGitHubAuthEnabled={true} />)
      expect(screen.getByText('Redirecting...')).toBeInTheDocument()

      // Test disabled state
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })
      rerender(<LoginPageContent isGitHubAuthEnabled={false} />)
      expect(screen.getByText('Signing In with GitHub is not enabled.')).toBeInTheDocument()
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('applies correct CSS classes for main container', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      const { container } = render(<LoginPageContent isGitHubAuthEnabled={true} />)

      // Find the main container (the outermost div with the flex classes)
      const mainContainer = container.firstChild as HTMLElement
      expect(mainContainer).toHaveClass('flex', 'min-h-[80vh]', 'items-center', 'justify-center')
    })

    it('applies correct CSS classes for login card', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      const loginCard = screen.getByText('Welcome back').closest('div')
      expect(loginCard).toHaveClass(
        'w-full',
        'max-w-sm',
        'flex',
        'flex-col',
        'gap-6',
        'rounded-2xl',
        'border',
        'border-gray-200',
        'bg-owasp-blue',
        'p-8',
        'shadow-xl',
        'dark:border-slate-700',
        'dark:bg-slate-800'
      )
    })

    it('applies correct CSS classes for sign-in button', () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      render(<LoginPageContent isGitHubAuthEnabled={true} />)

      const button = screen.getByRole('button', { name: /sign in with github/i })
      expect(button).toHaveClass(
        'flex',
        'w-full',
        'items-center',
        'justify-center',
        'gap-2',
        'rounded-lg',
        'bg-black',
        'px-4',
        'py-2',
        'font-medium',
        'text-white',
        'transition-colors',
        'hover:bg-gray-900/90'
      )
    })

    it('applies correct CSS classes for different states', () => {
      // Test loading state classes
      mockUseSession.mockReturnValue({
        status: userAuthStatus.LOADING as 'loading',
        data: null,
        update: jest.fn(),
      })

      const { rerender } = render(<LoginPageContent isGitHubAuthEnabled={true} />)
      let container = screen.getByText('Checking session...').closest('div')
      expect(container).toHaveClass(
        'flex',
        'min-h-[80vh]',
        'items-center',
        'justify-center',
        'gap-2'
      )

      // Test disabled state classes
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })
      rerender(<LoginPageContent isGitHubAuthEnabled={false} />)
      container = screen.getByText('Signing In with GitHub is not enabled.').closest('div')
      expect(container).toHaveClass('flex', 'min-h-[80vh]', 'items-center', 'justify-center')
    })
  })
})
