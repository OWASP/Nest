import { useQuery } from '@apollo/client/react'
import { mockActiveSubscription, mockNoSubscription } from '@mockData/mockSubscriptionData'
import { screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useSession } from 'next-auth/react'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import SettingsPage from 'app/settings/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useApolloClient: jest.fn(() => ({
    query: jest.fn().mockResolvedValue({ data: { searchProjects: [], searchChapters: [] } }),
  })),
  useQuery: jest.fn(),
  useMutation: jest.fn(() => [jest.fn(), { loading: false }]),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SettingsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })

  const mockUseQuery = useQuery as unknown as jest.Mock

  it('should have no violations when not subscribed', async () => {
    // Suppress debounced setSuggestions act() warning from EntityPicker
    jest.spyOn(console, 'error').mockImplementation((...args) => {
      if (typeof args[0] === 'string' && args[0].includes('not wrapped in act')) return
      throw new Error(`Console error: ${args.join(' ')}`)
    })
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { name: 'testuser' } },
      status: 'authenticated',
    })
    mockUseQuery.mockReturnValue({
      data: mockNoSubscription,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    const { container } = render(<SettingsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
    jest.restoreAllMocks()
  })

  it('should have no violations with active subscription', async () => {
    // Suppress debounced setSuggestions act() warning from EntityPicker
    jest.spyOn(console, 'error').mockImplementation((...args) => {
      if (typeof args[0] === 'string' && args[0].includes('not wrapped in act')) return
      throw new Error(`Console error: ${args.join(' ')}`)
    })
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { name: 'testuser' } },
      status: 'authenticated',
    })
    mockUseQuery.mockReturnValue({
      data: mockActiveSubscription,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    const { container } = render(<SettingsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
    jest.restoreAllMocks()
  })

  it('should have no violations in unauthenticated state', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'unauthenticated',
    })
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    const { container } = render(<SettingsPage />)

    expect(screen.getByText('Sign in required')).toBeInTheDocument()

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations in loading state', async () => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: null,
      status: 'loading',
    })

    const { container } = render(<SettingsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
