/* eslint-disable @typescript-eslint/naming-convention */
import { useQuery, useMutation } from '@apollo/client/react'
import { screen, waitFor, fireEvent, within } from '@testing-library/react'
import { mockApiKeys, mockCreateApiKeyResult } from '@unit/data/mockApiKeysData'
import { format, addDays } from 'date-fns'
import React from 'react'
import { render } from 'wrappers/testUtil'
import ApiKeysPage from 'app/settings/api-keys/page'
import {
  CreateApiKeyDocument,
  RevokeApiKeyDocument,
} from 'types/__generated__/apiKeyQueries.generated'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/modal', () => {
  const Stub = ({ children }: { children: React.ReactNode }) => <>{children}</>
  return {
    Modal: ({ isOpen, children }: { isOpen: boolean; children: React.ReactNode }) =>
      isOpen ? <div role="dialog">{children}</div> : null,
    ModalContent: Stub,
    ModalHeader: Stub,
    ModalBody: Stub,
    ModalFooter: Stub,
  }
})

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

beforeAll(() => {
  Object.defineProperty(navigator, 'clipboard', {
    value: { writeText: jest.fn() },
    writable: true,
  })
})

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

describe('ApiKeysPage Component', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseMutation = useMutation as unknown as jest.Mock
  const mockRefetch = jest.fn()
  const mockCreateMutation = jest.fn().mockResolvedValue(mockCreateApiKeyResult)
  const mockRevokeMutation = jest
    .fn()
    .mockResolvedValue({ data: { revokeApiKey: { success: true } } })

  beforeEach(() => {
    mockUseQuery.mockReturnValue({
      data: mockApiKeys,
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    mockUseMutation.mockImplementation((mutation) => {
      if (mutation === CreateApiKeyDocument) {
        return [mockCreateMutation, { loading: false }]
      }
      if (mutation === RevokeApiKeyDocument) {
        return [mockRevokeMutation, { loading: false }]
      }
      return [jest.fn(), { loading: false }]
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading skeleton initially', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: mockRefetch,
    })

    render(<ApiKeysPage />)

    expect(screen.queryByText('API Key Management')).not.toBeInTheDocument()

    const skeletonElements = document.querySelectorAll('.animate-pulse')
    expect(skeletonElements.length).toBeGreaterThan(0)
  })

  test('displays the list of API keys when data is fetched', async () => {
    const activeKeys = {
      apiKeys: mockApiKeys.apiKeys.filter((key) => !key.isRevoked),
    }

    mockUseQuery.mockReturnValue({
      data: activeKeys,
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    render(<ApiKeysPage />)

    await waitFor(() => {
      expect(screen.getByText('mock key 1')).toBeInTheDocument()
      expect(screen.getByText('mock key 2')).toBeInTheDocument()
      expect(screen.queryByText('revoked key')).not.toBeInTheDocument()
    })
  })

  test('displays a message when there are no API keys', async () => {
    mockUseQuery.mockReturnValue({
      data: { apiKeys: [] },
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    render(<ApiKeysPage />)

    await waitFor(() => {
      expect(screen.getByText("You don't have any API keys yet.")).toBeInTheDocument()
    })
  })

  test('displays error message when query fails', async () => {
    const errorMessage = 'Failed to fetch API keys'
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error(errorMessage),
      refetch: mockRefetch,
    })

    render(<ApiKeysPage />)

    await waitFor(() => {
      expect(screen.getByText('Error loading API keys')).toBeInTheDocument()
    })
  })

  test('allows a user to create a new API key', async () => {
    render(<ApiKeysPage />)
    fireEvent.click(screen.getByText(/Create New Key/))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    const nameInput = screen.getByLabelText('API Key Name')
    fireEvent.change(nameInput, { target: { value: 'Test New Key' } })
    fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

    await waitFor(() => {
      const expectedExpiry = addDays(new Date(), 30)
      const expectedVariables = {
        name: 'Test New Key',
        expiresAt: new Date(format(expectedExpiry, 'yyyy-MM-dd')),
      }

      expect(mockCreateMutation).toHaveBeenCalledWith({
        variables: expect.objectContaining({
          name: expectedVariables.name,
          expiresAt: expect.any(String),
        }),
      })
    })
  })

  test('handles API key creation with expiry date', async () => {
    render(<ApiKeysPage />)
    fireEvent.click(screen.getByText(/Create New Key/))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText('API Key Name'), {
      target: { value: 'Test Key with Expiry' },
    })
    const expiryInput = screen.getByLabelText('Expiration Date')
    fireEvent.change(expiryInput, {
      target: { value: '2025-12-31' },
    })
    fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

    await waitFor(() => {
      expect(mockCreateMutation).toHaveBeenCalledWith({
        variables: {
          name: 'Test Key with Expiry',
          expiresAt: new Date('2025-12-31T00:00:00.000Z').toISOString(),
        },
      })
    })
  })

  test('displays API key usage information', async () => {
    render(<ApiKeysPage />)
    await waitFor(() => {
      expect(screen.getByText('API Key Usage')).toBeInTheDocument()
      expect(screen.getByText(/Include your API key in the/)).toBeInTheDocument()
      expect(screen.getByText('X-API-Key')).toBeInTheDocument()
      expect(screen.getByText(/Keep your API keys secure/)).toBeInTheDocument()
    })
  })

  test('handles API key revocation', async () => {
    render(<ApiKeysPage />)
    const keyNameCell = await screen.findByText('mock key 1')
    const row = keyNameCell.closest('tr')
    expect(row).not.toBeNull()
    const revokeButton = within(row!).getByRole('button')
    fireEvent.click(revokeButton)
    const dialog = await screen.findByRole('dialog')
    expect(within(dialog).getByText('Revoke API Key')).toBeInTheDocument()
    expect(
      within(dialog).getByText(/Are you sure you want to revoke the key named/)
    ).toBeInTheDocument()
    const confirmRevokeButton = within(dialog).getByRole('button', { name: /Revoke Key/i })
    fireEvent.click(confirmRevokeButton)
    await waitFor(() => {
      expect(mockRevokeMutation).toHaveBeenCalledWith({
        variables: { uuid: '1' },
      })
    })
  })
})
