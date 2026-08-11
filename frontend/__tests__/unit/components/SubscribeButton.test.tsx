import { useMutation, useQuery } from '@apollo/client/react'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import SubscribeButton from 'components/SubscribeButton'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

jest.mock('next/link', () => {
  return function MockLink({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode
    href: string
    className?: string
    'aria-label'?: string
  }) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

describe('SubscribeButton', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseMutation = useMutation as unknown as jest.Mock
  const mockRefetch = jest.fn()
  const mockUpdateMutation = jest.fn()
  const mockCreateMutation = jest.fn()

  const defaultProps = {
    entityType: 'project' as const,
    entityId: '42',
    entityName: 'Test Project',
  }

  const setupMocks = ({
    session = 'authenticated',
    subscriptions = [] as Array<{
      id: string
      name: string
      frequency: string
      isActive: boolean
      subscribedProjects: Array<{ id: number; name: string }>
      subscribedChapters: Array<{ id: number; name: string }>
      subscribedCommittees: Array<{ id: number; name: string }>
    }>,
    createResult = {
      data: { createSnapshotSubscription: { ok: true, message: '' } },
    },
    updateResult = {
      data: { updateSnapshotSubscription: { ok: true, message: '' } },
    },
  }: {
    session?: string
    subscriptions?: Array<{
      id: string
      name: string
      frequency: string
      isActive: boolean
      subscribedProjects: Array<{ id: number; name: string }>
      subscribedChapters: Array<{ id: number; name: string }>
      subscribedCommittees: Array<{ id: number; name: string }>
    }>
    createResult?: {
      data: { createSnapshotSubscription: { ok: boolean; message: string } }
    }
    updateResult?: {
      data: { updateSnapshotSubscription: { ok: boolean; message: string } }
    }
  } = {}) => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { name: 'testuser' } },
      status: session,
    })

    mockUseQuery.mockReturnValue({
      data: { mySnapshotSubscriptions: subscriptions },
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    mockCreateMutation.mockResolvedValue(createResult)
    mockUpdateMutation.mockResolvedValue(updateResult)

    mockUseMutation.mockImplementation((_mutation, options) => {
      const wrappedFn = jest.fn(async (vars) => {
        // Determine which mock to use based on query name
        const isCreate = _mutation?.definitions?.[0]?.name?.value === 'CreateSnapshotSubscription'
        const result = isCreate ? await mockCreateMutation(vars) : await mockUpdateMutation(vars)
        if (options?.onCompleted) {
          options.onCompleted(result.data)
        }
        return result
      })
      return [wrappedFn, { loading: false }]
    })
  }

  beforeEach(() => jest.clearAllMocks())

  describe('Authentication', () => {
    test('returns null when not authenticated', () => {
      setupMocks({ session: 'unauthenticated' })
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.queryByText('Subscribe')).not.toBeInTheDocument()
      expect(screen.queryByText('Subscribed')).not.toBeInTheDocument()
    })

    test('returns null when session is loading', () => {
      setupMocks({ session: 'loading' })
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.queryByText('Subscribe')).not.toBeInTheDocument()
      expect(screen.queryByText('Subscribed')).not.toBeInTheDocument()
    })

    test('renders button when authenticated', () => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.getByText('Subscribe')).toBeInTheDocument()
    })
  })

  describe('Subscribe Button (not subscribed)', () => {
    test('renders Subscribe button with correct aria-label', () => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      const button = screen.getByText('Subscribe')
      expect(button).toBeInTheDocument()
      expect(button.closest('button')).toHaveAttribute('aria-label', 'Subscribe to Test Project')
    })

    test('opens modal when Subscribe is clicked', () => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
      expect(screen.getByText('Subscribe to Test Project')).toBeInTheDocument()
    })
  })

  describe('Subscribed State', () => {
    const subscribedMock = [
      {
        id: 'sub-1',
        name: 'My Digest',
        frequency: 'weekly',
        isActive: true,
        subscribedProjects: [{ id: 42, name: 'Test Project' }],
        subscribedChapters: [],
        subscribedCommittees: [],
      },
    ]

    test('renders Subscribed link when entity is in a subscription', () => {
      setupMocks({ subscriptions: subscribedMock })
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
    })

    test('Subscribed links to settings page', () => {
      setupMocks({ subscriptions: subscribedMock })
      render(<SubscribeButton {...defaultProps} />)
      const link = screen.getByText('Subscribed').closest('a')
      expect(link).toHaveAttribute('href', '/settings')
    })

    test('Subscribed has correct aria-label', () => {
      setupMocks({ subscriptions: subscribedMock })
      render(<SubscribeButton {...defaultProps} />)
      const link = screen.getByText('Subscribed').closest('a')
      expect(link).toHaveAttribute('aria-label', 'Subscribed to Test Project — click to manage')
    })
  })

  describe('Subscription Limit', () => {
    const maxSubscriptions = Array.from({ length: 5 }, (_, i) => ({
      id: `sub-${i}`,
      name: `Sub ${i}`,
      frequency: 'weekly',
      isActive: true,
      subscribedProjects: [{ id: i + 100, name: `Project ${i}` }],
      subscribedChapters: [],
      subscribedCommittees: [],
    }))

    test('disables subscribe button when limit reached', () => {
      setupMocks({ subscriptions: maxSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      const button = screen.getByText('Subscribe')
      expect(button.closest('button')).toBeDisabled()
    })

    test('shows limit reached aria-label when disabled', () => {
      setupMocks({ subscriptions: maxSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      const button = screen.getByText('Subscribe')
      expect(button.closest('button')).toHaveAttribute('aria-label', 'Subscription limit reached')
    })
  })

  describe('Subscribe Modal — Create New (no existing subscriptions)', () => {
    beforeEach(() => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
    })

    test('shows create form when no existing subscriptions', () => {
      expect(screen.getByText('Name')).toBeInTheDocument()
      expect(screen.getByText('Frequency')).toBeInTheDocument()
    })

    test('shows frequency options', () => {
      expect(screen.getByText('Weekly')).toBeInTheDocument()
      expect(screen.getByText('Monthly')).toBeInTheDocument()
    })

    test('switches frequency when clicked', () => {
      fireEvent.click(screen.getByText('Monthly'))
      const monthlyButton = screen.getByText('Monthly').closest('button')
      expect(monthlyButton).toHaveAttribute('aria-pressed', 'true')
      const weeklyButton = screen.getByText('Weekly').closest('button')
      expect(weeklyButton).toHaveAttribute('aria-pressed', 'false')
    })

    test('closes modal when Cancel is clicked', () => {
      fireEvent.click(screen.getByText('Cancel'))
      expect(screen.queryByText('Subscribe to Test Project')).not.toBeInTheDocument()
    })

    test('shows Create & Subscribe button', () => {
      expect(screen.getByText('Create & Subscribe')).toBeInTheDocument()
    })
  })

  describe('Subscribe Modal — List View (existing subscriptions)', () => {
    const existingSubscriptions = [
      {
        id: 'sub-1',
        name: 'My Weekly Digest',
        frequency: 'weekly',
        isActive: true,
        subscribedProjects: [],
        subscribedChapters: [],
        subscribedCommittees: [],
      },
      {
        id: 'sub-2',
        name: 'Monthly Security',
        frequency: 'monthly',
        isActive: true,
        subscribedProjects: [],
        subscribedChapters: [],
        subscribedCommittees: [],
      },
    ]

    test('shows list of existing subscriptions', () => {
      setupMocks({ subscriptions: existingSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      expect(screen.getByText('My Weekly Digest')).toBeInTheDocument()
      expect(screen.getByText('Monthly Security')).toBeInTheDocument()
    })

    test('shows Add to Subscription button', () => {
      setupMocks({ subscriptions: existingSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      expect(screen.getByText('Add to Subscription')).toBeInTheDocument()
    })

    test('shows Create New Subscription option', () => {
      setupMocks({ subscriptions: existingSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      expect(screen.getByText('Create New Subscription')).toBeInTheDocument()
    })

    test('shows Subscribed link when entity is already in a subscription', () => {
      const subsWithEntity = [
        {
          ...existingSubscriptions[0],
          subscribedProjects: [{ id: 42, name: 'Test Project' }],
        },
        existingSubscriptions[1],
      ]
      setupMocks({ subscriptions: subsWithEntity })
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
    })
  })

  describe('Create Subscription via Modal', () => {
    test('calls create mutation when creating new subscription', async () => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      fireEvent.click(screen.getByText('Create & Subscribe'))

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalled()
      })
    })

    test('shows success toast on successful creation', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
      fireEvent.click(screen.getByText('Create & Subscribe'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Subscribed!',
            color: 'success',
          })
        )
      })
    })

    test('shows error toast on failed creation', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({
        createResult: {
          data: { createSnapshotSubscription: { ok: false, message: 'Limit reached' } },
        },
      })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
      fireEvent.click(screen.getByText('Create & Subscribe'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            color: 'danger',
          })
        )
      })
    })
  })

  describe('Entity Type Matching', () => {
    test('detects subscription for chapter entity type', () => {
      setupMocks({
        subscriptions: [
          {
            id: 'sub-1',
            name: 'My Sub',
            frequency: 'weekly',
            isActive: true,
            subscribedProjects: [],
            subscribedChapters: [{ id: 42, name: 'Test Chapter' }],
            subscribedCommittees: [],
          },
        ],
      })
      render(<SubscribeButton entityType="chapter" entityId="42" entityName="Test Chapter" />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
    })

    test('detects subscription for committee entity type', () => {
      setupMocks({
        subscriptions: [
          {
            id: 'sub-1',
            name: 'My Sub',
            frequency: 'monthly',
            isActive: true,
            subscribedProjects: [],
            subscribedChapters: [],
            subscribedCommittees: [{ id: 42, name: 'Test Committee' }],
          },
        ],
      })
      render(<SubscribeButton entityType="committee" entityId="42" entityName="Test Committee" />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
    })

    test('does not show subscribed for different entity id', () => {
      setupMocks({
        subscriptions: [
          {
            id: 'sub-1',
            name: 'My Sub',
            frequency: 'weekly',
            isActive: true,
            subscribedProjects: [{ id: 99, name: 'Other Project' }],
            subscribedChapters: [],
            subscribedCommittees: [],
          },
        ],
      })
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.getByText('Subscribe')).toBeInTheDocument()
      expect(screen.queryByText('Subscribed')).not.toBeInTheDocument()
    })
  })

  describe('Relay ID Decoding', () => {
    test('handles base64-encoded relay IDs', () => {
      const base64Id = btoa('ProjectType:42')
      setupMocks({
        subscriptions: [
          {
            id: 'sub-1',
            name: 'My Sub',
            frequency: 'weekly',
            isActive: true,
            subscribedProjects: [{ id: 42, name: 'Test Project' }],
            subscribedChapters: [],
            subscribedCommittees: [],
          },
        ],
      })
      render(<SubscribeButton {...defaultProps} entityId={base64Id} />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
    })
  })

  describe('Update Subscription via Modal', () => {
    const existingSubscriptions = [
      {
        id: 'sub-1',
        name: 'My Weekly Digest',
        frequency: 'weekly',
        isActive: true,
        subscribedProjects: [],
        subscribedChapters: [],
        subscribedCommittees: [],
      },
    ]

    test('calls update mutation when adding to existing subscription', async () => {
      setupMocks({ subscriptions: existingSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      fireEvent.click(screen.getByText('My Weekly Digest'))
      fireEvent.click(screen.getByText('Add to Subscription'))

      await waitFor(() => {
        expect(mockUpdateMutation).toHaveBeenCalled()
      })
    })

    test('shows success toast on successful update', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({ subscriptions: existingSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
      fireEvent.click(screen.getByText('My Weekly Digest'))
      fireEvent.click(screen.getByText('Add to Subscription'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Added!',
            color: 'success',
          })
        )
      })
    })

    test('shows error toast on failed update', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({
        subscriptions: existingSubscriptions,
        updateResult: {
          data: { updateSnapshotSubscription: { ok: false, message: 'Update failed' } },
        },
      })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
      fireEvent.click(screen.getByText('My Weekly Digest'))
      fireEvent.click(screen.getByText('Add to Subscription'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            color: 'danger',
          })
        )
      })
    })

    test('shows error toast on network failure during update', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({ subscriptions: existingSubscriptions })
      mockUseMutation.mockImplementation((_mutation, options) => {
        const wrappedFn = jest.fn(async () => {
          if (options?.onError) {
            options.onError(new Error('Network error'))
          }
          return { data: null }
        })
        return [wrappedFn, { loading: false }]
      })

      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
      fireEvent.click(screen.getByText('My Weekly Digest'))
      fireEvent.click(screen.getByText('Add to Subscription'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            description: 'Failed to update subscription.',
            color: 'danger',
          })
        )
      })
    })
  })

  describe('Modal View Switching', () => {
    test('switches from list to create and back', () => {
      setupMocks({
        subscriptions: [
          {
            id: 'sub-1',
            name: 'My Sub',
            frequency: 'weekly',
            isActive: true,
            subscribedProjects: [],
            subscribedChapters: [],
            subscribedCommittees: [],
          },
        ],
      })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      fireEvent.click(screen.getByText('Create New Subscription'))
      expect(screen.getByText('Name')).toBeInTheDocument()

      fireEvent.click(screen.getByText('← Back to existing subscriptions'))
      expect(screen.getByText('My Sub')).toBeInTheDocument()
      expect(screen.queryByText('Name')).not.toBeInTheDocument()
    })
  })

  describe('Network Error Handling', () => {
    test('shows error toast on network failure', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      ;(useSession as jest.Mock).mockReturnValue({
        data: { user: { name: 'testuser' } },
        status: 'authenticated',
      })

      mockUseQuery.mockReturnValue({
        data: { mySnapshotSubscriptions: [] },
        loading: false,
        error: null,
        refetch: mockRefetch,
      })

      mockUseMutation.mockImplementation((_mutation, options) => {
        const wrappedFn = jest.fn(async () => {
          if (options?.onError) {
            options.onError(new Error('Network error'))
          }
          return { data: null }
        })
        return [wrappedFn, { loading: false }]
      })

      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      fireEvent.click(screen.getByText('Create & Subscribe'))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            description: 'Failed to create subscription.',
            color: 'danger',
          })
        )
      })
    })
  })
})
