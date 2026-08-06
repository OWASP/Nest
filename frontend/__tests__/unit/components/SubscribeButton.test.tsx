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
  const mockCreateMutation = jest.fn()

  const defaultProps = {
    entityType: 'project' as const,
    entityId: '42',
    entityName: 'Test Project',
  }

  const setupMocks = ({
    session = 'authenticated',
    subscriptions = [],
    createResult = { data: { createEntitySubscription: { ok: true, message: '' } } },
  }: {
    session?: string
    subscriptions?: Array<{
      id: string
      frequency: string
      isActive: boolean
      project?: { id: string; name: string } | null
      chapter?: { id: string; name: string } | null
      committee?: { id: string; name: string } | null
    }>
    createResult?: {
      data: { createEntitySubscription: { ok: boolean; message: string } }
    }
  } = {}) => {
    ;(useSession as jest.Mock).mockReturnValue({
      data: { user: { name: 'testuser' } },
      status: session,
    })

    mockUseQuery.mockReturnValue({
      data: { myEntitySubscriptions: subscriptions },
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    mockCreateMutation.mockResolvedValue(createResult)

    mockUseMutation.mockImplementation((_mutation, options) => {
      const wrappedFn = jest.fn(async (vars) => {
        const result = await mockCreateMutation(vars)
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
    test('renders Subscribe button with bell icon', () => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      const button = screen.getByText('Subscribe')
      expect(button).toBeInTheDocument()
      expect(button).toHaveAttribute('aria-label', 'Subscribe to Test Project')
    })

    test('opens modal when Subscribe is clicked', () => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
      expect(screen.getByText('Subscribe to updates from Test Project')).toBeInTheDocument()
    })
  })

  describe('Subscribed State', () => {
    const subscribedMock = [
      {
        id: 'sub-1',
        frequency: 'weekly',
        isActive: true,
        project: { id: '42', name: 'Test Project' },
        chapter: null,
        committee: null,
      },
    ]

    test('renders Subscribed link when already subscribed', () => {
      setupMocks({ subscriptions: subscribedMock })
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
    })

    test('Subscribed links to settings page with entity tab', () => {
      setupMocks({ subscriptions: subscribedMock })
      render(<SubscribeButton {...defaultProps} />)
      const link = screen.getByText('Subscribed').closest('a')
      expect(link).toHaveAttribute('href', '/settings?tab=entity')
    })

    test('Subscribed has correct aria-label', () => {
      setupMocks({ subscriptions: subscribedMock })
      render(<SubscribeButton {...defaultProps} />)
      const link = screen.getByText('Subscribed').closest('a')
      expect(link).toHaveAttribute('aria-label', 'Subscribed to Test Project — click to manage')
    })
  })

  describe('Inactive Subscription State', () => {
    const inactiveMock = [
      {
        id: 'sub-1',
        frequency: 'weekly',
        isActive: false,
        project: { id: '42', name: 'Test Project' },
        chapter: null,
        committee: null,
      },
    ]

    test('renders Manage link when subscription is inactive', () => {
      setupMocks({ subscriptions: inactiveMock })
      render(<SubscribeButton {...defaultProps} />)
      expect(screen.getByText('Manage')).toBeInTheDocument()
      expect(screen.queryByText('Subscribe')).not.toBeInTheDocument()
    })

    test('Manage links to settings page', () => {
      setupMocks({ subscriptions: inactiveMock })
      render(<SubscribeButton {...defaultProps} />)
      const link = screen.getByText('Manage').closest('a')
      expect(link).toHaveAttribute('href', '/settings?tab=entity')
    })

    test('Manage has correct aria-label', () => {
      setupMocks({ subscriptions: inactiveMock })
      render(<SubscribeButton {...defaultProps} />)
      const link = screen.getByText('Manage').closest('a')
      expect(link).toHaveAttribute('aria-label', 'Manage inactive subscription for Test Project')
    })
  })

  describe('Subscription Limit', () => {
    const maxSubscriptions = Array.from({ length: 5 }, (_, i) => ({
      id: `sub-${i}`,
      frequency: 'weekly',
      isActive: true,
      project: { id: `${i + 100}`, name: `Project ${i}` },
      chapter: null,
      committee: null,
    }))

    test('disables subscribe button when limit reached', () => {
      setupMocks({ subscriptions: maxSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      const button = screen.getByText('Subscribe')
      expect(button).toBeDisabled()
    })

    test('shows limit reached tooltip when disabled', () => {
      setupMocks({ subscriptions: maxSubscriptions })
      render(<SubscribeButton {...defaultProps} />)
      const button = screen.getByText('Subscribe')
      expect(button).toHaveAttribute('aria-label', 'Subscription limit reached')
    })
  })

  describe('Subscribe Modal', () => {
    beforeEach(() => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))
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
      expect(screen.queryByText('Subscribe to updates from Test Project')).not.toBeInTheDocument()
    })
  })

  describe('Create Subscription', () => {
    test('calls create mutation with correct variables', async () => {
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      // Find the Subscribe button inside the modal (not the trigger)
      const modalButtons = screen.getAllByText('Subscribe')
      const submitButton = modalButtons[modalButtons.length - 1]
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith({
          variables: {
            inputData: {
              entityType: 'project',
              entityId: 42,
              frequency: 'weekly',
            },
          },
        })
      })
    })

    test('shows success toast on successful subscription', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks()
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      const modalButtons = screen.getAllByText('Subscribe')
      fireEvent.click(modalButtons[modalButtons.length - 1])

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Subscribed!',
            color: 'success',
          })
        )
      })
    })

    test('shows error toast on failed subscription', async () => {
      const { addToast } = jest.requireMock('@heroui/toast')
      setupMocks({
        createResult: {
          data: { createEntitySubscription: { ok: false, message: 'Limit reached' } },
        },
      })
      render(<SubscribeButton {...defaultProps} />)
      fireEvent.click(screen.getByText('Subscribe'))

      const modalButtons = screen.getAllByText('Subscribe')
      fireEvent.click(modalButtons[modalButtons.length - 1])

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
            frequency: 'weekly',
            isActive: true,
            project: null,
            chapter: { id: '42', name: 'Test Chapter' },
            committee: null,
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
            frequency: 'monthly',
            isActive: true,
            project: null,
            chapter: null,
            committee: { id: '42', name: 'Test Committee' },
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
            frequency: 'weekly',
            isActive: true,
            project: { id: '99', name: 'Other Project' },
            chapter: null,
            committee: null,
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
            frequency: 'weekly',
            isActive: true,
            project: { id: base64Id, name: 'Test Project' },
            chapter: null,
            committee: null,
          },
        ],
      })
      render(<SubscribeButton {...defaultProps} entityId={base64Id} />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
    })

    test('handles non-decodable IDs gracefully', () => {
      setupMocks({
        subscriptions: [
          {
            id: 'sub-1',
            frequency: 'weekly',
            isActive: true,
            project: { id: 'not-a-number-or-base64!!!', name: 'Test Project' },
            chapter: null,
            committee: null,
          },
        ],
      })
      render(<SubscribeButton {...defaultProps} entityId="not-a-number-or-base64!!!" />)
      expect(screen.getByText('Subscribed')).toBeInTheDocument()
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
        data: { myEntitySubscriptions: [] },
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

      const modalButtons = screen.getAllByText('Subscribe')
      fireEvent.click(modalButtons[modalButtons.length - 1])

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
