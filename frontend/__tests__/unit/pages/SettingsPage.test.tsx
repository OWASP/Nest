import { useQuery, useMutation } from '@apollo/client/react'
import {
  mockActiveSubscription,
  mockCancelSubscriptionResult,
  mockCreateSubscriptionResult,
  mockNoSubscription,
  mockUpdateSubscriptionResult,
} from '@mockData/mockSubscriptionData'
import { screen, fireEvent } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import SettingsPage from 'app/settings/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useApolloClient: jest.fn(() => ({
    query: jest.fn().mockResolvedValue({ data: { searchProjects: [], searchChapters: [] } }),
  })),
  useQuery: jest.fn(),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

describe('SettingsPage Component', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseMutation = useMutation as unknown as jest.Mock
  const mockRefetch = jest.fn()
  const mockCreateMutation = jest.fn()
  const mockUpdateMutation = jest.fn()
  const mockCancelMutation = jest.fn()

  const setupMocks = (
    queryOverrides = {},
    sessionOverrides: { status: string } = { status: 'authenticated' }
  ) => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { name: 'testuser' } },
      ...sessionOverrides,
    })

    mockUseQuery.mockReturnValue({
      data: mockNoSubscription,
      loading: false,
      error: null,
      refetch: mockRefetch,
      ...queryOverrides,
    })

    mockCreateMutation.mockResolvedValue(mockCreateSubscriptionResult)
    mockUpdateMutation.mockResolvedValue(mockUpdateSubscriptionResult)
    mockCancelMutation.mockResolvedValue(mockCancelSubscriptionResult)

    mockUseMutation.mockImplementation((_mutation, options) => {
      const wrappedFn = jest.fn(async (vars) => {
        let result
        if (options?.onCompleted) {
          if (
            _mutation ===
            jest.requireActual('server/queries/subscriptionQueries')?.CREATE_SNAPSHOT_SUBSCRIPTION
          ) {
            result = await mockCreateMutation(vars)
          } else if (
            _mutation ===
            jest.requireActual('server/queries/subscriptionQueries')?.UPDATE_SNAPSHOT_SUBSCRIPTION
          ) {
            result = await mockUpdateMutation(vars)
          } else {
            result = await mockCancelMutation(vars)
          }
          options.onCompleted(result.data)
        }
        return result
      })
      return [wrappedFn, { loading: false }]
    })
  }

  beforeEach(() => setupMocks())
  afterEach(() => jest.clearAllMocks())

  describe('Authentication States', () => {
    test('shows loading spinner when session is loading', () => {
      setupMocks({}, { status: 'loading' })
      render(<SettingsPage />)
      expect(screen.queryByText('Settings')).not.toBeInTheDocument()
    })

    test('shows sign in required when unauthenticated', () => {
      setupMocks({}, { status: 'unauthenticated' })
      render(<SettingsPage />)
      expect(screen.getByText('Sign in required')).toBeInTheDocument()
      expect(screen.getByText('Please sign in to manage your settings.')).toBeInTheDocument()
    })

    test('shows settings page when authenticated', () => {
      setupMocks()
      render(<SettingsPage />)
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })
  })

  describe('Tab Navigation', () => {
    test('renders Subscriptions tab', () => {
      setupMocks()
      render(<SettingsPage />)
      expect(screen.getByText('Subscriptions')).toBeInTheDocument()
    })
  })

  describe('Not Subscribed State', () => {
    test('shows Not Subscribed status', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Not Subscribed')).toBeInTheDocument()
      expect(
        screen.getByText(
          'Subscribe to get curated OWASP community updates delivered to your inbox.'
        )
      ).toBeInTheDocument()
    })

    test('shows Choose Frequency heading when not subscribed', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Choose Frequency')).toBeInTheDocument()
    })

    test('shows Subscribe button when not subscribed', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Subscribe')).toBeInTheDocument()
    })

    test('renders frequency options (Weekly and Monthly)', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Weekly')).toBeInTheDocument()
      expect(screen.getByText('Monthly')).toBeInTheDocument()
    })

    test('renders global content preference toggles', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('General Subscriptions')).toBeInTheDocument()
      expect(screen.getAllByText('Chapters').length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText('Events')).toBeInTheDocument()
      expect(screen.getByText('Posts')).toBeInTheDocument()
      expect(screen.getByText('Users')).toBeInTheDocument()
    })

    test('renders Project Subscriptions section', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Project Subscriptions')).toBeInTheDocument()
    })

    test('renders Chapter Subscriptions section when chapters enabled', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Chapter Subscriptions')).toBeInTheDocument()
    })
  })

  describe('Active Subscription State', () => {
    test('shows Subscription Active status', () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Subscription Active')).toBeInTheDocument()
    })

    test('shows Frequency heading when subscribed', () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Frequency')).toBeInTheDocument()
    })

    test('shows Save Changes and Unsubscribe buttons', () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Save Changes')).toBeInTheDocument()
      expect(screen.getByText('Unsubscribe')).toBeInTheDocument()
    })

    test('displays current frequency in status message', () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('weekly')).toBeInTheDocument()
    })

    test('displays project preference cards for subscribed projects', () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)
      expect(screen.getAllByText('OWASP Nest').length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Frequency Selection', () => {
    test('can switch between Weekly and Monthly', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)

      fireEvent.click(screen.getByText('Monthly'))

      expect(screen.getByText('Monthly')).toBeInTheDocument()
      expect(screen.getByText('Weekly')).toBeInTheDocument()
    })
  })

  describe('Loading State', () => {
    test('shows loading spinner when query is loading', () => {
      setupMocks({ loading: true })
      render(<SettingsPage />)
      expect(screen.queryByText('Not Subscribed')).not.toBeInTheDocument()
      expect(screen.queryByText('Subscription Active')).not.toBeInTheDocument()
    })
  })

  describe('Description Text', () => {
    test('shows correct description for General Subscriptions', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Manage your general OWASP subscriptions.')).toBeInTheDocument()
    })

    test('shows correct description for Project Subscriptions', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(
        screen.getByText(/Add projects and choose which content types.*you want from each one/)
      ).toBeInTheDocument()
    })

    test('shows correct description for Chapter Subscriptions', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText(/Optionally select specific chapters to follow/)).toBeInTheDocument()
    })
  })
})
