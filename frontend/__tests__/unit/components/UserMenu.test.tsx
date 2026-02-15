import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useLogout } from 'hooks/useLogout'
import { signIn } from 'next-auth/react'
import React from 'react'
import { ExtendedSession } from 'types/auth'
import UserMenu from 'components/UserMenu'

// Mock next-auth
jest.mock('next-auth/react', () => ({
  signIn: jest.fn(),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(),
}))

// Mock useLogout hook
jest.mock('hooks/useLogout', () => ({
  useLogout: jest.fn(),
}))

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    className,
    height,
    width,
    ...props
  }: {
    src: string
    alt: string
    className?: string
    height?: number
    width?: number
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} className={className} height={height} width={width} {...props} />
  ),
}))

// Add this react-icons mock for FaGithub:
jest.mock('react-icons/fa', () => ({
  FaGithub: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="github-icon" {...props} />,
}))

describe('UserMenu Component', () => {
  const mockUseSession = useDjangoSession as jest.MockedFunction<typeof useDjangoSession>
  const mockSignIn = signIn as jest.MockedFunction<typeof signIn>
  const mockUseLogout = useLogout as jest.MockedFunction<typeof useLogout>

  const mockLogout = jest.fn()
  const defaultLogoutReturn = {
    logout: mockLogout,
    isLoggingOut: false,
  }

  const mockSession: ExtendedSession = {
    user: {
      name: 'John Doe',
      email: 'john@example.com',
      image: 'https://example.com/avatar.jpg',
      isOwaspStaff: true,
    },
    expires: '2024-12-31',
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseLogout.mockReturnValue(defaultLogoutReturn)
    mockSignIn.mockResolvedValue(undefined)
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders nothing when GitHub auth is disabled', () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'authenticated',
      })

      const { container } = render(<UserMenu isGitHubAuthEnabled={false} />)
      expect(container.firstChild).toBeNull()
    })

    it('renders with GitHub auth enabled', () => {
      mockUseSession.mockReturnValue({
        session: { user: null, expires: '2024-12-31' },
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)
      expect(screen.getByRole('button')).toBeInTheDocument()
    })
  })

  describe('Conditional rendering logic', () => {
    it('renders loading state when session status is loading', () => {
      mockUseSession.mockReturnValue({
        isSyncing: true,
        session: null,
        status: 'loading',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const loadingElement = document.querySelector('.animate-pulse')
      expect(loadingElement).toBeInTheDocument()
      expect(loadingElement).toHaveClass('h-10', 'w-10', 'rounded-full')
    })

    it('renders sign in button when user is not authenticated', () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'unauthenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const signInButton = screen.getByRole('button')
      expect(signInButton).toHaveTextContent('Sign In')
      expect(screen.getByTestId('github-icon')).toBeInTheDocument()
    })

    it('renders user avatar and dropdown when user is authenticated', () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      expect(avatarButton).toHaveAttribute('aria-haspopup', 'true')

      const avatar = screen.getByAltText('User avatar')
      expect(avatar).toHaveAttribute('src', mockSession.user.image)
    })

    it('shows dropdown menu when user avatar is clicked', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'true')
      })

      expect(screen.getByText('Sign out')).toBeInTheDocument()
    })
  })

  describe('Prop-based behavior', () => {
    it('returns null when isGitHubAuthEnabled is false regardless of session state', () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      const { container } = render(<UserMenu isGitHubAuthEnabled={false} />)
      expect(container.firstChild).toBeNull()
    })

    it('shows different UI based on authentication status', () => {
      // Test unauthenticated state
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'unauthenticated',
      })

      const { rerender } = render(<UserMenu isGitHubAuthEnabled={true} />)
      expect(screen.getByText('Sign In')).toBeInTheDocument()

      // Test authenticated state
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      rerender(<UserMenu isGitHubAuthEnabled={true} />)
      expect(screen.getByAltText('User avatar')).toBeInTheDocument()
      expect(screen.queryByText('Sign In')).not.toBeInTheDocument()
    })
  })

  describe('Event handling', () => {
    it('calls signIn when sign in button is clicked', async () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'unauthenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const signInButton = screen.getByRole('button')
      fireEvent.click(signInButton)

      expect(mockSignIn).toHaveBeenCalledWith('github', {
        callbackUrl: '/',
        prompt: 'login',
      })
    })

    it('toggles dropdown when avatar button is clicked', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')

      // Initially closed
      expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      expect(screen.queryByText('Sign out')).not.toBeInTheDocument()

      // Click to open
      fireEvent.click(avatarButton)
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'true')
      })
      expect(screen.getByText('Sign out')).toBeInTheDocument()

      // Click to close
      fireEvent.click(avatarButton)
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      })
      expect(screen.queryByText('Sign out')).not.toBeInTheDocument()
    })

    it('calls logout and closes dropdown when sign out is clicked', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      // Open dropdown
      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })

      // Click sign out
      const signOutButton = screen.getByText('Sign out')
      fireEvent.click(signOutButton)

      expect(mockLogout).toHaveBeenCalledTimes(1)
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      })
    })

    it('closes dropdown when clicking outside', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(
        <div>
          <UserMenu isGitHubAuthEnabled={true} />
          <div data-testid="outside-element">Outside</div>
        </div>
      )

      // Open dropdown
      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'true')
      })

      // Click outside
      const outsideElement = screen.getByTestId('outside-element')
      fireEvent.mouseDown(outsideElement)

      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      })
    })

    it('does not close dropdown when clicking inside the dropdown', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      // Open dropdown
      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'true')
      })

      // Get dropdown element - mocking getElementById since aria-controls logic relies on it
      const dropdownId = avatarButton.getAttribute('aria-controls')
      // Note: In JSDOM with React Testing Library, getElementById works if element is in document
      // The dropdown is rendered conditionally, so it should be there now
      const dropdown = document.getElementById(dropdownId!)
      expect(dropdown).toBeInTheDocument()

      // Click inside (e.g. on the dropdown div itself)
      fireEvent.mouseDown(dropdown!)

      // Should still be open
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'true')
      })
    })

    it('handles mousedown events gracefully when safely syncing (ref is null)', () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: true, // This causes early return, so ref is not attached
        status: 'loading',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      // Fire mousedown on document (should not crash)
      fireEvent.mouseDown(document.body)

      // No assertions needed other than it doesn't crash,
      // but we can assert loading state to be sure we rendered correctly
      expect(document.querySelector('.animate-pulse')).toBeInTheDocument()
    })
  })

  describe('State changes / internal logic', () => {
    it('manages dropdown open/close state correctly', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')

      // Test multiple open/close cycles
      for (let i = 0; i < 3; i++) {
        fireEvent.click(avatarButton)
        await waitFor(() => {
          expect(avatarButton).toHaveAttribute('aria-expanded', 'true')
        })

        fireEvent.click(avatarButton)
        await waitFor(() => {
          expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
        })
      }
    })

    it('handles logout state correctly', async () => {
      // First render with normal state to open dropdown
      mockUseLogout.mockReturnValue({
        logout: mockLogout,
        isLoggingOut: false,
      })

      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      const { rerender } = render(<UserMenu isGitHubAuthEnabled={true} />)

      // Open dropdown first
      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      // Wait for dropdown to open
      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })

      // Now simulate logout state
      mockUseLogout.mockReturnValue({
        logout: mockLogout,
        isLoggingOut: true,
      })

      rerender(<UserMenu isGitHubAuthEnabled={true} />)

      // Avatar button should be disabled during logout
      expect(avatarButton).toBeDisabled()

      // The dropdown should show "Signing out..." text
      await waitFor(() => {
        expect(screen.getByText('Signing out...')).toBeInTheDocument()
      })

      const signOutButton = screen.getByText('Signing out...')
      expect(signOutButton).toBeDisabled()
    })
  })

  describe('Default values and fallbacks', () => {
    it('uses default avatar when user image is not available', () => {
      const sessionWithoutImage = {
        ...mockSession,
        user: {
          ...mockSession.user,
          image: null,
        },
      }

      mockUseSession.mockReturnValue({
        session: sessionWithoutImage,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatar = screen.getByAltText('User avatar')
      expect(avatar).toHaveAttribute('src', '/default-avatar.png')
    })

    it('uses default avatar when user image is undefined', () => {
      const sessionWithUndefinedImage = {
        ...mockSession,
        user: {
          ...mockSession.user,
          image: undefined,
        },
      }

      mockUseSession.mockReturnValue({
        session: sessionWithUndefinedImage,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatar = screen.getByAltText('User avatar')
      expect(avatar).toHaveAttribute('src', '/default-avatar.png')
    })
  })

  describe('Text and content rendering', () => {
    it('renders correct sign in button text and icon', () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'unauthenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const signInButton = screen.getByRole('button')
      expect(signInButton).toHaveTextContent('Sign In')
      expect(screen.getByTestId('github-icon')).toBeInTheDocument()
    })

    it('renders correct sign out button text', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      // Open dropdown
      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })
    })

    it('renders signing out text when logging out', async () => {
      // First render with normal state to open dropdown
      mockUseLogout.mockReturnValue({
        logout: mockLogout,
        isLoggingOut: false,
      })

      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      const { rerender } = render(<UserMenu isGitHubAuthEnabled={true} />)

      // Open dropdown first
      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      // Wait for dropdown to open
      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })

      // Now simulate logout state
      mockUseLogout.mockReturnValue({
        logout: mockLogout,
        isLoggingOut: true,
      })

      rerender(<UserMenu isGitHubAuthEnabled={true} />)

      await waitFor(() => {
        expect(screen.getByText('Signing out...')).toBeInTheDocument()
      })
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles null session gracefully', () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'unauthenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('handles undefined session gracefully', () => {
      mockUseSession.mockReturnValue({
        session: undefined,
        isSyncing: false,
        status: 'unauthenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('handles session with null user gracefully', () => {
      mockUseSession.mockReturnValue({
        session: { user: null, expires: '2024-12-31' },
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatar = screen.getByAltText('User avatar')
      expect(avatar).toHaveAttribute('src', '/default-avatar.png')
    })

    it('handles rapid clicking without breaking', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')

      // Rapid clicks
      fireEvent.click(avatarButton)
      fireEvent.click(avatarButton)
      fireEvent.click(avatarButton)
      fireEvent.click(avatarButton)

      // Should still work correctly
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      })
    })
  })

  describe('Accessibility roles and labels', () => {
    it('has correct ARIA attributes for dropdown button', () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      expect(avatarButton).toHaveAttribute('aria-haspopup', 'true')
      expect(avatarButton).toHaveAttribute('aria-controls')
    })

    it('updates aria-expanded when dropdown opens/closes', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')

      expect(avatarButton).toHaveAttribute('aria-expanded', 'false')

      fireEvent.click(avatarButton)
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'true')
      })

      fireEvent.click(avatarButton)
      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      })
    })

    it('has correct alt text for avatar image', () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatar = screen.getByAltText('User avatar')
      expect(avatar).toBeInTheDocument()
    })

    it('dropdown has correct id that matches aria-controls', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        const dropdownId = avatarButton.getAttribute('aria-controls')
        expect(dropdownId).not.toBeNull()
        const dropdown = document.getElementById(dropdownId)
        expect(dropdown).toBeInTheDocument()
      })
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('applies correct CSS classes to sign in button', () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'unauthenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const signInButton = screen.getByRole('button')
      expect(signInButton).toHaveClass(
        'group',
        'relative',
        'cursor-pointer',
        'flex',
        'h-10',
        'items-center',
        'justify-center',
        'gap-2',
        'rounded-md',
        'bg-[#87a1bc]',
        'p-4',
        'text-sm',
        'font-medium',
        'text-black',
        'hover:ring-1',
        'hover:ring-[#b0c7de]',
        'dark:bg-slate-900',
        'dark:text-white',
        'dark:hover:bg-slate-900/90',
        'dark:hover:ring-[#46576b]'
      )
    })

    it('applies correct CSS classes to loading state', () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: true,
        status: 'unauthenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const loadingContainer = document.querySelector('.flex.h-10.w-10.items-center.justify-center')
      expect(loadingContainer).toBeInTheDocument()

      const loadingSpinner = document.querySelector('.animate-pulse.h-10.w-10.rounded-full')
      expect(loadingSpinner).toBeInTheDocument()
    })

    it('applies correct CSS classes to avatar container', () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const container = screen.getByRole('button').parentElement
      expect(container).toHaveClass('relative', 'flex', 'items-center', 'justify-center')

      const avatarButton = screen.getByRole('button')
      expect(avatarButton).toHaveClass('w-auto', 'focus:outline-hidden')
    })

    it('applies correct CSS classes to dropdown menu', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        const dropdownId = avatarButton.getAttribute('aria-controls')
        expect(dropdownId).not.toBeNull()
        const dropdown = document.getElementById(dropdownId)
        expect(dropdown).toHaveClass(
          'absolute',
          'right-0',
          'top-full',
          'z-20',
          'mt-2',
          'w-48',
          'overflow-hidden',
          'rounded-md',
          'bg-white',
          'shadow-lg',
          'dark:bg-slate-800'
        )
      })
    })

    it('applies correct CSS classes to sign out button', async () => {
      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        const signOutButton = screen.getByText('Sign out')
        expect(signOutButton).toHaveClass(
          'block',
          'w-full',
          'px-4',
          'py-2',
          'text-left',
          'text-sm',
          'font-medium'
        )
      })
    })
  })

  describe('Cleanup and memory leaks', () => {
    it('removes event listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener')

      mockUseSession.mockReturnValue({
        session: mockSession,
        isSyncing: false,
        status: 'authenticated',
      })

      const { unmount } = render(<UserMenu isGitHubAuthEnabled={true} />)

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function))

      removeEventListenerSpy.mockRestore()
    })
  })

  describe('Project Leader and OWASP Staff links', () => {
    it('closes dropdown when My Mentorship link is clicked', async () => {
      const leaderSession: ExtendedSession = {
        user: {
          name: 'Leader User',
          email: 'leader@example.com',
          image: 'https://example.com/avatar.jpg',
          isLeader: true,
          isOwaspStaff: false,
        },
        expires: '2024-12-31',
      }

      mockUseSession.mockReturnValue({
        session: leaderSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        expect(screen.getByText('My Mentorship')).toBeInTheDocument()
      })

      const mentorshipLink = screen.getByText('My Mentorship')
      fireEvent.click(mentorshipLink)

      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      })
    })

    it('closes dropdown when Project Health Dashboard link is clicked', async () => {
      const staffSession: ExtendedSession = {
        user: {
          name: 'Staff User',
          email: 'staff@example.com',
          image: 'https://example.com/avatar.jpg',
          isLeader: false,
          isOwaspStaff: true,
        },
        expires: '2024-12-31',
      }

      mockUseSession.mockReturnValue({
        session: staffSession,
        isSyncing: false,
        status: 'authenticated',
      })

      render(<UserMenu isGitHubAuthEnabled={true} />)

      const avatarButton = screen.getByRole('button')
      fireEvent.click(avatarButton)

      await waitFor(() => {
        expect(screen.getByText('Project Health Dashboard')).toBeInTheDocument()
      })

      const dashboardLink = screen.getByText('Project Health Dashboard')
      fireEvent.click(dashboardLink)

      await waitFor(() => {
        expect(avatarButton).toHaveAttribute('aria-expanded', 'false')
      })
    })
  })
})
