import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useSession } from 'next-auth/react'
import { userAuthStatus } from 'utils/constants'
import LoginPageContent from 'components/LoginPageContent'

// mock dependency
jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
  signIn: jest.fn(),
}))

describe('LoginPage a11y', () => {
  const mockUseSession = useSession as jest.MockedFunction<typeof useSession>

  describe('when GitHub auth is enabled', () => {
    it('should not have any accessibility violations', async () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })

      const { container } = render(<LoginPageContent isGitHubAuthEnabled />)

      const results = await axe(container)

      expect(results).toHaveNoViolations()
    })
  })

  describe('when GitHub auth is disabled', () => {
    it('should not have any accessibility violations when loading', async () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.LOADING as 'loading',
        data: null,
        update: jest.fn(),
      })
      const { container } = render(<LoginPageContent isGitHubAuthEnabled={false} />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('should not have any accessibility violations when authenticated', async () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.AUTHENTICATED as 'authenticated',
        data: null,
        update: jest.fn(),
      })
      const { container } = render(<LoginPageContent isGitHubAuthEnabled={false} />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('should not have any accessibility violations when unauthenticated', async () => {
      mockUseSession.mockReturnValue({
        status: userAuthStatus.UNAUTHENTICATED as 'unauthenticated',
        data: null,
        update: jest.fn(),
      })
      const { container } = render(<LoginPageContent isGitHubAuthEnabled={false} />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})
