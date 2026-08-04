import { useQuery, useMutation } from '@apollo/client/react'
import {
  mockActiveSubscription,
  mockCancelEntitySubscriptionResult,
  mockCancelSubscriptionResult,
  mockCreateEntitySubscriptionResult,
  mockCreateSubscriptionResult,
  mockDeleteEntitySubscriptionResult,
  mockEntitySubscriptions,
  mockInactiveEntitySubscriptions,
  mockNoEntitySubscriptions,
  mockNoSubscription,
  mockReactivateEntitySubscriptionResult,
  mockUpdateEntitySubscriptionResult,
  mockUpdateSubscriptionResult,
} from '@mockData/mockSubscriptionData'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import SettingsPage from 'app/settings/page'
import {
  CANCEL_ENTITY_SUBSCRIPTION,
  CANCEL_SNAPSHOT_SUBSCRIPTION,
  CREATE_ENTITY_SUBSCRIPTION,
  CREATE_SNAPSHOT_SUBSCRIPTION,
  DELETE_ENTITY_SUBSCRIPTION,
  REACTIVATE_ENTITY_SUBSCRIPTION,
  UPDATE_ENTITY_SUBSCRIPTION,
  UPDATE_SNAPSHOT_SUBSCRIPTION,
} from 'server/queries/subscriptionQueries'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useApolloClient: jest.fn(() => ({
    query: jest.fn().mockResolvedValue({
      data: { searchProjects: [], searchChapters: [], searchCommittees: [] },
    }),
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

const mockSearchParamsGet = jest.fn()
jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useSearchParams: jest.fn(() => ({
    get: mockSearchParamsGet,
  })),
}))

describe('SettingsPage Component', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseMutation = useMutation as unknown as jest.Mock
  const mockRefetch = jest.fn()

  const mockCreateMutation = jest.fn()
  const mockUpdateMutation = jest.fn()
  const mockCancelMutation = jest.fn()

  const mockCreateEntityMutation = jest.fn()
  const mockUpdateEntityMutation = jest.fn()
  const mockCancelEntityMutation = jest.fn()
  const mockDeleteEntityMutation = jest.fn()
  const mockReactivateEntityMutation = jest.fn()

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

    // Setup snapshot mutation results
    mockCreateMutation.mockResolvedValue(mockCreateSubscriptionResult)
    mockUpdateMutation.mockResolvedValue(mockUpdateSubscriptionResult)
    mockCancelMutation.mockResolvedValue(mockCancelSubscriptionResult)

    // Setup entity mutation results
    mockCreateEntityMutation.mockResolvedValue(mockCreateEntitySubscriptionResult)
    mockUpdateEntityMutation.mockResolvedValue(mockUpdateEntitySubscriptionResult)
    mockCancelEntityMutation.mockResolvedValue(mockCancelEntitySubscriptionResult)
    mockDeleteEntityMutation.mockResolvedValue(mockDeleteEntitySubscriptionResult)
    mockReactivateEntityMutation.mockResolvedValue(mockReactivateEntitySubscriptionResult)

    mockUseMutation.mockImplementation((mutation, options) => {
      const wrappedFn = jest.fn(async (vars) => {
        let result
        if (mutation === CREATE_SNAPSHOT_SUBSCRIPTION) {
          result = await mockCreateMutation(vars)
        } else if (mutation === UPDATE_SNAPSHOT_SUBSCRIPTION) {
          result = await mockUpdateMutation(vars)
        } else if (mutation === CANCEL_SNAPSHOT_SUBSCRIPTION) {
          result = await mockCancelMutation(vars)
        } else if (mutation === CREATE_ENTITY_SUBSCRIPTION) {
          result = await mockCreateEntityMutation(vars)
        } else if (mutation === UPDATE_ENTITY_SUBSCRIPTION) {
          result = await mockUpdateEntityMutation(vars)
        } else if (mutation === CANCEL_ENTITY_SUBSCRIPTION) {
          result = await mockCancelEntityMutation(vars)
        } else if (mutation === DELETE_ENTITY_SUBSCRIPTION) {
          result = await mockDeleteEntityMutation(vars)
        } else if (mutation === REACTIVATE_ENTITY_SUBSCRIPTION) {
          result = await mockReactivateEntityMutation(vars)
        } else {
          result = { data: {} }
        }
        if (options?.onCompleted) {
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

    test('renders Snapshot and Entity sub-tabs', () => {
      setupMocks()
      render(<SettingsPage />)
      expect(screen.getByText('Snapshot')).toBeInTheDocument()
      expect(screen.getByText('Entity')).toBeInTheDocument()
    })

    test('switches to Entity tab when clicked', () => {
      setupMocks()
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByText('Entity Subscriptions')).toBeInTheDocument()
    })

    test('opens Entity tab directly when ?tab=entity is in URL', () => {
      mockSearchParamsGet.mockImplementation((key: string) => {
        if (key === 'tab') return 'entity'
        return null
      })
      setupMocks({ data: mockNoEntitySubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText('Entity Subscriptions')).toBeInTheDocument()
      mockSearchParamsGet.mockReturnValue(null)
    })
  })

  describe('Snapshot Tab - Not Subscribed State', () => {
    test('shows not subscribed description', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(
        screen.getByText(
          'Subscribe to get curated OWASP community updates delivered to your inbox.'
        )
      ).toBeInTheDocument()
    })

    test.each([['Snapshot Subscription'], ['Subscribe'], ['Content']])(
      'renders %s when not subscribed',
      (text) => {
        setupMocks({ data: mockNoSubscription })
        render(<SettingsPage />)
        expect(screen.getByText(text)).toBeInTheDocument()
      }
    )

    test('renders frequency options (Weekly and Monthly)', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Weekly')).toBeInTheDocument()
      expect(screen.getByText('Monthly')).toBeInTheDocument()
    })

    test('renders all 8 content preference toggles', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Content')).toBeInTheDocument()
      expect(screen.getByText('Chapters')).toBeInTheDocument()
      expect(screen.getByText('Events')).toBeInTheDocument()
      expect(screen.getByText('Issues')).toBeInTheDocument()
      expect(screen.getByText('Posts')).toBeInTheDocument()
      expect(screen.getByText('Projects')).toBeInTheDocument()
      expect(screen.getByText('Pull Requests')).toBeInTheDocument()
      expect(screen.getByText('Releases')).toBeInTheDocument()
      expect(screen.getByText('Users')).toBeInTheDocument()
    })
  })

  describe('Snapshot Tab - Active Subscription State', () => {
    test.each([['Active'], ['Frequency'], ['Weekly']])('renders %s when subscribed', (text) => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)
      expect(screen.getByText(text)).toBeInTheDocument()
    })

    test('shows Save Changes and Unsubscribe buttons', () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)
      expect(screen.getByText('Save Changes')).toBeInTheDocument()
      expect(screen.getByText('Unsubscribe')).toBeInTheDocument()
    })
  })

  describe('Snapshot - Frequency Selection', () => {
    test('can switch between Weekly and Monthly', () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)

      fireEvent.click(screen.getByText('Monthly'))

      expect(screen.getByText('Monthly')).toBeInTheDocument()
      expect(screen.getByText('Weekly')).toBeInTheDocument()
    })
  })

  describe('Snapshot - Mutation Payload', () => {
    test('Subscribe sends correct default variables', async () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)

      fireEvent.click(screen.getByText('Subscribe'))

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith({
          variables: {
            inputData: {
              frequency: 'weekly',
              includeChapters: true,
              includeEvents: true,
              includeIssues: true,
              includePosts: true,
              includeProjects: true,
              includePullRequests: true,
              includeReleases: true,
              includeUsers: true,
            },
          },
        })
      })
    })

    test('Subscribe sends selected frequency', async () => {
      setupMocks({ data: mockNoSubscription })
      render(<SettingsPage />)

      fireEvent.click(screen.getByText('Monthly'))
      fireEvent.click(screen.getByText('Subscribe'))

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: expect.objectContaining({
              inputData: expect.objectContaining({ frequency: 'monthly' }),
            }),
          })
        )
      })
    })

    test('Save Changes sends correct variables for active subscription', async () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)

      fireEvent.click(screen.getByText('Save Changes'))

      await waitFor(() => {
        expect(mockUpdateMutation).toHaveBeenCalledWith({
          variables: {
            inputData: {
              frequency: 'weekly',
              includeChapters: true,
              includeEvents: true,
              includeIssues: true,
              includePosts: true,
              includeProjects: true,
              includePullRequests: true,
              includeReleases: true,
              includeUsers: true,
            },
          },
        })
      })
    })

    test('Unsubscribe calls cancel mutation', async () => {
      setupMocks({ data: mockActiveSubscription })
      render(<SettingsPage />)

      fireEvent.click(screen.getByText('Unsubscribe'))

      await waitFor(() => {
        expect(screen.getByText('Confirm Unsubscribe')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Yes, Unsubscribe'))

      await waitFor(() => {
        expect(mockCancelMutation).toHaveBeenCalled()
      })
    })
  })

  describe('Entity Tab - Empty State', () => {
    test('shows empty message when no entity subscriptions', () => {
      setupMocks({ data: mockNoEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByText('No entity subscriptions yet.')).toBeInTheDocument()
    })

    test('shows subscription count', () => {
      setupMocks({ data: mockNoEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByText(/0\/5 subscriptions used/)).toBeInTheDocument()
    })
  })

  describe('Entity Tab - Active Subscription', () => {
    test('renders subscription name and entity preferences', () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
    })

    test('shows Unsubscribe and Save Changes buttons for active subscriptions', () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      const unsubscribeButtons = screen.getAllByText('Unsubscribe')
      expect(unsubscribeButtons.length).toBeGreaterThan(0)
      const saveButtons = screen.getAllByText('Save Changes')
      expect(saveButtons.length).toBeGreaterThan(0)
    })

    test('shows trash icon for permanent delete', () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      const trashButtons = screen.getAllByLabelText('Delete subscription permanently')
      expect(trashButtons.length).toBeGreaterThan(0)
    })

    test('shows active subscription count', () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByText(/2\/5 subscriptions used/)).toBeInTheDocument()
    })
  })

  describe('Entity Tab - Inactive Subscription', () => {
    test('shows Reactivate button for inactive subscriptions', () => {
      setupMocks({ data: mockInactiveEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByText('Reactivate')).toBeInTheDocument()
    })

    test('shows trash icon for inactive subscriptions', () => {
      setupMocks({ data: mockInactiveEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByLabelText('Delete subscription permanently')).toBeInTheDocument()
    })

    test('does not count inactive subscriptions toward limit', () => {
      setupMocks({ data: mockInactiveEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      expect(screen.getByText(/0\/5 subscriptions used/)).toBeInTheDocument()
    })
  })

  describe('Entity Tab - Unsubscribe Flow', () => {
    test('opens confirmation modal when clicking Unsubscribe', () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      const unsubscribeButtons = screen.getAllByText('Unsubscribe')
      fireEvent.click(unsubscribeButtons[0])

      expect(screen.getByText('Confirm Unsubscribe')).toBeInTheDocument()
      expect(
        screen.getByText(
          'Are you sure you want to unsubscribe? You will no longer receive snapshot digest emails.'
        )
      ).toBeInTheDocument()
    })

    test('closes modal when Cancel is clicked', () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      const unsubscribeButtons = screen.getAllByText('Unsubscribe')
      fireEvent.click(unsubscribeButtons[0])

      const cancelButtons = screen.getAllByText('Cancel')
      fireEvent.click(cancelButtons[cancelButtons.length - 1])

      expect(screen.queryByText('Confirm Unsubscribe')).not.toBeInTheDocument()
    })

    test('calls cancel mutation when Yes, Unsubscribe is clicked', async () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      const unsubscribeButtons = screen.getAllByText('Unsubscribe')
      fireEvent.click(unsubscribeButtons[0])
      fireEvent.click(screen.getByText('Yes, Unsubscribe'))

      await waitFor(() => {
        expect(mockCancelEntityMutation).toHaveBeenCalled()
      })
    })
  })

  describe('Entity Tab - Delete Flow', () => {
    test('opens delete confirmation modal when clicking trash icon', () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      const trashButtons = screen.getAllByLabelText('Delete subscription permanently')
      fireEvent.click(trashButtons[0])

      expect(screen.getByText('Confirm Delete')).toBeInTheDocument()
    })

    test('calls delete mutation when Yes, Delete is clicked', async () => {
      setupMocks({ data: mockEntitySubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Entity'))
      const trashButtons = screen.getAllByLabelText('Delete subscription permanently')
      fireEvent.click(trashButtons[0])
      fireEvent.click(screen.getByText('Yes, Delete'))

      await waitFor(() => {
        expect(mockDeleteEntityMutation).toHaveBeenCalled()
      })
    })
  })

  describe('Loading State', () => {
    test('shows loading spinner when query is loading', () => {
      setupMocks({ loading: true })
      render(<SettingsPage />)
      expect(screen.queryByText('Snapshot Subscription')).not.toBeInTheDocument()
      expect(screen.queryByText('Active')).not.toBeInTheDocument()
    })
  })
})
