import { useQuery, useMutation } from '@apollo/client/react'
import {
  mockActiveSubscriptions,
  mockCreateSubscriptionResult,
  mockDeleteSubscriptionResult,
  mockMultipleSubscriptions,
  mockNoSubscriptions,
  mockUpdateSubscriptionResult,
} from '@mockData/mockSubscriptionData'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import { render } from 'wrappers/testUtil'
import SettingsPage from 'app/settings/page'
import {
  CREATE_SNAPSHOT_SUBSCRIPTION,
  DELETE_SNAPSHOT_SUBSCRIPTION,
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

describe('SettingsPage Component', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseMutation = useMutation as unknown as jest.Mock
  const mockRefetch = jest.fn()

  const mockCreateMutation = jest.fn()
  const mockUpdateMutation = jest.fn()
  const mockDeleteMutation = jest.fn()

  const setupMocks = (
    queryOverrides = {},
    sessionOverrides: { status: string } = { status: 'authenticated' }
  ) => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { name: 'testuser' } },
      ...sessionOverrides,
    })

    mockUseQuery.mockReturnValue({
      data: mockNoSubscriptions,
      loading: false,
      error: null,
      refetch: mockRefetch,
      ...queryOverrides,
    })

    mockCreateMutation.mockResolvedValue(mockCreateSubscriptionResult)
    mockUpdateMutation.mockResolvedValue(mockUpdateSubscriptionResult)
    mockDeleteMutation.mockResolvedValue(mockDeleteSubscriptionResult)

    mockUseMutation.mockImplementation((mutation, options) => {
      const wrappedFn = jest.fn(async (vars) => {
        let result
        if (mutation === CREATE_SNAPSHOT_SUBSCRIPTION) {
          result = await mockCreateMutation(vars)
        } else if (mutation === UPDATE_SNAPSHOT_SUBSCRIPTION) {
          result = await mockUpdateMutation(vars)
        } else if (mutation === DELETE_SNAPSHOT_SUBSCRIPTION) {
          result = await mockDeleteMutation(vars)
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
      expect(screen.getAllByText('Subscriptions').length).toBeGreaterThan(0)
    })
  })

  describe('Empty State', () => {
    test('shows empty message when no subscriptions', () => {
      setupMocks({ data: mockNoSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText('No subscriptions yet.')).toBeInTheDocument()
    })

    test('shows subscription count as 0', () => {
      setupMocks({ data: mockNoSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText(/0\/5 active/)).toBeInTheDocument()
    })

    test('shows New Subscription button', () => {
      setupMocks({ data: mockNoSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText('New Subscription')).toBeInTheDocument()
    })
  })

  describe('Active Subscription Card', () => {
    test('renders subscription name', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByDisplayValue('My Weekly Digest')).toBeInTheDocument()
    })

    test('renders Active badge', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText('Active')).toBeInTheDocument()
    })

    test('renders frequency and content toggles', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText('Frequency')).toBeInTheDocument()
      expect(screen.getByText('Content')).toBeInTheDocument()
      expect(screen.getByText('Weekly')).toBeInTheDocument()
    })

    test('renders entity multi-selects', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      expect(screen.getAllByText('Projects').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Chapters').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Committees').length).toBeGreaterThan(0)
    })

    test('renders subscribed entity chips', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText('OWASP Nest')).toBeInTheDocument()
      expect(screen.getByText('OWASP Aarhus')).toBeInTheDocument()
    })

    test('shows Save Changes and Delete buttons', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText('Save Changes')).toBeInTheDocument()
      expect(screen.getByText('Delete')).toBeInTheDocument()
    })

    test('shows subscription count', () => {
      setupMocks({ data: mockMultipleSubscriptions })
      render(<SettingsPage />)
      expect(screen.getByText(/2\/5 active/)).toBeInTheDocument()
    })

    test('renders all 8 content toggles', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      const contentToggles = screen.getAllByRole('button', { pressed: true })
      expect(contentToggles.length).toBeGreaterThanOrEqual(8)
      expect(screen.getAllByText('Chapters').length).toBeGreaterThan(0)
      expect(screen.getByText('Events')).toBeInTheDocument()
      expect(screen.getByText('Issues')).toBeInTheDocument()
      expect(screen.getByText('Posts')).toBeInTheDocument()
      expect(screen.getAllByText('Projects').length).toBeGreaterThan(0)
      expect(screen.getByText('Pull Requests')).toBeInTheDocument()
      expect(screen.getByText('Releases')).toBeInTheDocument()
      expect(screen.getByText('Users')).toBeInTheDocument()
    })
  })

  describe('Delete Flow', () => {
    test('opens delete confirmation modal when clicking Delete button', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Delete'))
      expect(screen.getByText('Confirm Delete')).toBeInTheDocument()
    })

    test('closes modal when Cancel is clicked', () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Delete'))
      const cancelButtons = screen.getAllByText('Cancel')
      fireEvent.click(cancelButtons[cancelButtons.length - 1])
      expect(screen.queryByText('Confirm Delete')).not.toBeInTheDocument()
    })

    test('calls delete mutation when Yes, Delete is clicked', async () => {
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)
      const deleteButtons = screen.getAllByText('Delete')
      fireEvent.click(deleteButtons[0])
      fireEvent.click(screen.getAllByText('Delete')[1])

      await waitFor(() => {
        expect(mockDeleteMutation).toHaveBeenCalled()
      })
    })
  })

  describe('Create Subscription Flow', () => {
    test('shows create form when New Subscription is clicked', () => {
      setupMocks({ data: mockNoSubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('New Subscription'))
      expect(screen.getByText('Name')).toBeInTheDocument()
      expect(screen.getByText('Create Subscription')).toBeInTheDocument()
    })

    test('disables Create button when no content toggles are selected', () => {
      setupMocks({ data: mockNoSubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('New Subscription'))

      const createButton = screen.getByText('Create Subscription').closest('button')
      expect(createButton).toBeDisabled()
    })

    test('calls create mutation with name and frequency', async () => {
      setupMocks({ data: mockNoSubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('New Subscription'))

      fireEvent.change(screen.getByPlaceholderText('e.g., My Weekly Digest'), {
        target: { value: 'Test Sub' },
      })

      const contentToggles = screen.getAllByRole('button', { pressed: false })
      const chaptersToggle = contentToggles.find((btn) => btn.textContent?.includes('Chapters'))
      if (chaptersToggle) fireEvent.click(chaptersToggle)

      fireEvent.click(screen.getByText('Create Subscription'))

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith(
          expect.objectContaining({
            variables: expect.objectContaining({
              inputData: expect.objectContaining({
                name: 'Test Sub',
                frequency: 'weekly',
                includeChapters: true,
              }),
            }),
          })
        )
      })
    })
  })

  describe('Loading State', () => {
    test('shows loading spinner when query is loading', () => {
      setupMocks({ loading: true })
      render(<SettingsPage />)
      expect(
        screen.queryByText('Manage your OWASP community update subscriptions.')
      ).not.toBeInTheDocument()
    })
  })
})
