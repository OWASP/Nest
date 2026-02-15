import { fireEvent, render, screen } from '@testing-library/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useLogout } from 'hooks/useLogout'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { ReactNode } from 'react'
import UserMenu from 'components/UserMenu'

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(),
}))

jest.mock('hooks/useLogout', () => ({
  useLogout: jest.fn(),
}))

jest.mock(
  'next/link',
  () =>
    ({
      children,
      href,
      ...props
    }: {
      children: ReactNode
      href: string
      [key: string]: unknown
    }) => (
      <a href={href} {...props}>
        {children}
      </a>
    )
)

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('UserMenu Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  const mockUseSession = useDjangoSession as jest.MockedFunction<typeof useDjangoSession>
  const mockUseLogout = useLogout as jest.MockedFunction<typeof useLogout>

  it('should not have any accessibility violations when syncing', async () => {
    mockUseSession.mockReturnValue({
      session: null,
      isSyncing: true,
      status: 'loading',
    })
    mockUseLogout.mockReturnValue({
      logout: jest.fn(),
      isLoggingOut: false,
    })

    const { container } = render(<UserMenu isGitHubAuthEnabled={true} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  describe('when unauthenticated', () => {
    it('should not have any accessibility violations', async () => {
      mockUseSession.mockReturnValue({
        session: null,
        isSyncing: false,
        status: 'unauthenticated',
      })
      mockUseLogout.mockReturnValue({
        logout: jest.fn(),
        isLoggingOut: false,
      })

      const { container } = render(<UserMenu isGitHubAuthEnabled={true} />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })

  describe('when authenticated', () => {
    describe('isOpen is true', () => {
      it('should not have any accessibility violations when user is project leader', async () => {
        mockUseSession.mockReturnValue({
          session: {
            user: {
              name: 'John Doe',
              email: 'john@example.com',
              image: 'https://example.com/avatar.jpg',
              isLeader: true,
            },
            expires: '2024-12-31',
          },
          isSyncing: false,
          status: 'authenticated',
        })
        mockUseLogout.mockReturnValue({
          logout: jest.fn(),
          isLoggingOut: false,
        })

        const { container } = render(<UserMenu isGitHubAuthEnabled={true} />)

        const button = screen.getByRole('button')
        fireEvent.click(button)

        const results = await axe(container)
        expect(results).toHaveNoViolations()
      })

      it('should not have any accessibility violations when user is owasp staff', async () => {
        mockUseSession.mockReturnValue({
          session: {
            user: {
              name: 'John Doe',
              email: 'john@example.com',
              image: 'https://example.com/avatar.jpg',
              isOwaspStaff: true,
            },
            expires: '2024-12-31',
          },
          isSyncing: false,
          status: 'authenticated',
        })
        mockUseLogout.mockReturnValue({
          logout: jest.fn(),
          isLoggingOut: false,
        })

        const { container } = render(<UserMenu isGitHubAuthEnabled={true} />)

        const button = screen.getByRole('button')
        fireEvent.click(button)

        const results = await axe(container)
        expect(results).toHaveNoViolations()
      })
    })
  })
})
