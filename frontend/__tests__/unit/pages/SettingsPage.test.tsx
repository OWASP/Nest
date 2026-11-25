import { useApolloClient, useQuery, useMutation } from '@apollo/client/react'
import {
  mockActiveSubscriptions,
  mockCreateSubscriptionResult,
  mockDeleteSubscriptionResult,
  mockMultipleSubscriptions,
  mockNoSubscriptions,
  mockUpdateSubscriptionResult,
} from '@mockData/mockSubscriptionData'
import { act, screen, fireEvent, waitFor, within } from '@testing-library/react'
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
      expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
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

      const dialog = screen.getByRole('dialog')
      const confirmDeleteButton = within(dialog).getByRole('button', { name: 'Delete' })
      fireEvent.click(confirmDeleteButton)

      await waitFor(() => {
        expect(mockDeleteMutation).toHaveBeenCalledWith({ variables: { subscriptionId: 1 } })
      })
    })

    test('shows an error and skips the mutation when the subscription ID cannot be decoded', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({
        data: {
          mySnapshotSubscriptions: [
            { ...mockActiveSubscriptions.mySnapshotSubscriptions[0], id: 'not-a-relay-id!' },
          ],
        },
      })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('Delete'))
      const dialog = screen.getByRole('dialog')
      fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Failed to delete subscription.',
          color: 'danger',
        })
      })
      expect(mockDeleteMutation).not.toHaveBeenCalled()
    })
  })

  describe('Update Subscription Flow', () => {
    test('saves edited subscription with full update variables and refetches', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({ data: mockActiveSubscriptions })
      render(<SettingsPage />)

      fireEvent.change(screen.getByDisplayValue('My Weekly Digest'), {
        target: { value: 'Renamed Digest' },
      })
      fireEvent.click(screen.getByRole('button', { name: 'Monthly' }))
      fireEvent.click(screen.getByRole('button', { name: 'Events' }))
      fireEvent.click(screen.getByRole('button', { name: 'Remove OWASP Aarhus' }))

      fireEvent.click(screen.getByRole('button', { name: 'Save Changes' }))

      await waitFor(() => {
        expect(mockUpdateMutation).toHaveBeenCalledWith({
          variables: {
            subscriptionId: 1,
            inputData: {
              name: 'Renamed Digest',
              frequency: 'monthly',
              includeChapters: true,
              includeEvents: false,
              includeIssues: true,
              includePosts: true,
              includeProjects: true,
              includePullRequests: true,
              includeReleases: true,
              includeUsers: true,
              projectIds: [1],
              chapterIds: [],
              committeeIds: [],
            },
          },
        })
      })
      expect(addToast).toHaveBeenCalledWith({
        title: 'Updated',
        description: 'Your preferences have been saved.',
        color: 'success',
      })
      expect(mockRefetch).toHaveBeenCalled()
    })

    test('shows error toast when update returns ok: false', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({ data: mockActiveSubscriptions })
      mockUpdateMutation.mockResolvedValue({
        data: { updateSnapshotSubscription: { ok: false, message: 'Update failed' } },
      })
      render(<SettingsPage />)

      fireEvent.click(screen.getByRole('button', { name: 'Save Changes' }))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Update failed',
          color: 'danger',
        })
      })
      expect(mockRefetch).not.toHaveBeenCalled()
    })

    test('shows an error and skips the mutation when the subscription ID cannot be decoded', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({
        data: {
          mySnapshotSubscriptions: [
            { ...mockActiveSubscriptions.mySnapshotSubscriptions[0], id: 'not-a-relay-id!' },
          ],
        },
      })
      render(<SettingsPage />)

      fireEvent.click(screen.getByRole('button', { name: 'Save Changes' }))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Failed to update subscription.',
          color: 'danger',
        })
      })
      expect(mockUpdateMutation).not.toHaveBeenCalled()
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
      expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
      expect(
        screen.queryByText(/Manage your OWASP community update subscriptions/)
      ).not.toBeInTheDocument()
    })
  })

  describe('Entity Search', () => {
    const mockUseApolloClient = useApolloClient as unknown as jest.Mock
    let defaultUseApolloClient: ReturnType<typeof mockUseApolloClient.getMockImplementation>

    beforeEach(() => {
      defaultUseApolloClient = mockUseApolloClient.getMockImplementation()
    })

    afterEach(() => {
      mockUseApolloClient.mockImplementation(defaultUseApolloClient)
    })

    test('ignores an in-flight response once the search query has changed', async () => {
      let resolveStale: (value: unknown) => void = () => {}
      const query = jest
        .fn()
        .mockImplementationOnce(
          () =>
            new Promise((resolve) => {
              resolveStale = resolve
            })
        )
        .mockResolvedValueOnce({
          data: { searchProjects: [{ id: btoa('ProjectNode:20'), name: 'OWASP Fresh Result' }] },
        })
      const client = { query }
      mockUseApolloClient.mockImplementation(() => client)

      setupMocks({ data: mockNoSubscriptions })
      render(<SettingsPage />)
      fireEvent.click(screen.getByText('New Subscription'))

      const input = screen.getByRole('combobox', { name: 'Projects' })
      act(() => input.focus())
      fireEvent.change(input, { target: { value: 'ow' } })
      await waitFor(() => expect(query).toHaveBeenCalledTimes(1))

      fireEvent.change(input, { target: { value: 'owasp' } })
      await waitFor(() => expect(query).toHaveBeenCalledTimes(2))
      expect(await screen.findByText('OWASP Fresh Result')).toBeInTheDocument()

      await act(async () => {
        resolveStale({
          data: { searchProjects: [{ id: btoa('ProjectNode:10'), name: 'OWASP Stale Result' }] },
        })
      })

      expect(screen.getByText('OWASP Fresh Result')).toBeInTheDocument()
      expect(screen.queryByText('OWASP Stale Result')).not.toBeInTheDocument()
    })
  })
})
