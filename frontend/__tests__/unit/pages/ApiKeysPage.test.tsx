/* eslint-disable @typescript-eslint/naming-convention */
import { useQuery, useMutation } from '@apollo/client'
import { screen, waitFor, fireEvent, within } from '@testing-library/react'
import { mockApiKeys, mockCreateApiKeyResult } from '@unit/data/mockApiKeysData'
import React from 'react'
import { render } from 'wrappers/testUtil'
import ApiKeysPage from 'app/settings/api-keys/page'
import { CREATE_API_KEY, GET_API_KEYS, REVOKE_API_KEY } from 'server/queries/apiKeyQueries'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
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
  const mockUseQuery = useQuery as jest.Mock
  const mockUseMutation = useMutation as jest.Mock

  beforeEach(() => {
    mockUseQuery.mockReturnValue({
      data: mockApiKeys,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    mockUseMutation.mockImplementation((mutation) => {
      if (mutation === CREATE_API_KEY) {
        return [jest.fn().mockResolvedValue(mockCreateApiKeyResult), { loading: false }]
      }
      if (mutation === REVOKE_API_KEY) {
        return [
          jest.fn().mockResolvedValue({ data: { revokeApiKey: { success: true } } }),
          { loading: false },
        ]
      }
      return [jest.fn(), { loading: false }]
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading skeleton initially', async () => {
    ;(useQuery as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: jest.fn(),
    })
    render(<ApiKeysPage />)
    expect(screen.getByText('API Key Management')).toBeInTheDocument()
    expect(screen.getAllByTestId('mock-icon')).toHaveLength(2)
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
      refetch: jest.fn(),
    })

    render(<ApiKeysPage />)

    await waitFor(() => {
      expect(screen.getByText('mock key 1')).toBeInTheDocument()
      expect(screen.getByText('...SmQs')).toBeInTheDocument()
      expect(screen.getByText('mock key 2')).toBeInTheDocument()
      expect(screen.getByText('...feh4')).toBeInTheDocument()
      expect(screen.queryByText('revoked key')).not.toBeInTheDocument()
    })
  })

  test('displays a message when there are no API keys', async () => {
    mockUseQuery.mockReturnValue({
      data: { apiKeys: [] },
      loading: false,
      error: null,
      refetch: jest.fn(),
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
      error: { message: errorMessage },
      refetch: jest.fn(),
    })

    render(<ApiKeysPage />)

    await waitFor(() => {
      expect(screen.getByText(`Error: ${errorMessage}`)).toBeInTheDocument()
    })
  })

  test('allows a user to create a new API key', async () => {
    const mockCreateFn = jest.fn()
    const mockRefetch = jest.fn()

    mockUseQuery.mockReturnValue({
      data: { apiKeys: [] },
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    mockUseMutation.mockImplementation((mutation) => {
      if (mutation === CREATE_API_KEY) {
        return [
          (variables) => {
            mockCreateFn(variables)
            return Promise.resolve(mockCreateApiKeyResult)
          },
          { loading: false },
        ]
      }
      return [jest.fn(), { loading: false }]
    })
    render(<ApiKeysPage />)
    fireEvent.click(screen.getByText('Create New Key'))
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
    const nameInput = screen.getByLabelText('API Key Name')
    fireEvent.change(nameInput, { target: { value: 'Test New Key' } })
    fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalledWith({
        variables: { name: 'Test New Key' },
      })
    })
  })

  test('handles API key creation with expiry date', async () => {
    const mockCreateFn = jest.fn()

    mockUseMutation.mockImplementation((mutation) => {
      if (mutation === CREATE_API_KEY) {
        return [mockCreateFn, { loading: false }]
      }
      return [jest.fn(), { loading: false }]
    })
    render(<ApiKeysPage />)
    fireEvent.click(screen.getByText('Create New Key'))
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
    fireEvent.change(screen.getByLabelText('API Key Name'), {
      target: { value: 'Test Key with Expiry' },
    })
    const expiryInput = screen.getByLabelText('Expiration Date (Optional)')
    fireEvent.change(expiryInput, {
      target: { value: '2025-12-31' },
    })
    fireEvent.click(screen.getByRole('button', { name: /create api key/i }))
    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalledWith({
        variables: {
          name: 'Test Key with Expiry',
          expiresAt: new Date('2025-12-31'),
        },
      })
    })
  })

  test('fetches and displays revoked keys when checkbox is checked', async () => {
    const mockRefetch = jest.fn()

    mockUseQuery.mockReturnValue({
      data: { apiKeys: mockApiKeys.apiKeys.filter((key) => !key.isRevoked) },
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    render(<ApiKeysPage />)
    await waitFor(() => {
      expect(screen.queryByText('revoked key')).not.toBeInTheDocument()
    })
    const checkbox = screen.getByLabelText('Show revoked keys')
    fireEvent.click(checkbox)
    expect(mockUseQuery).toHaveBeenCalledWith(
      GET_API_KEYS,
      expect.objectContaining({
        variables: { includeRevoked: true },
      })
    )
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

  test('handles API key creation', async () => {
    const mockCreateFn = jest.fn().mockResolvedValue(mockCreateApiKeyResult)
    const mockRefetch = jest.fn()

    mockUseQuery.mockReturnValue({
      data: { apiKeys: [] },
      loading: false,
      error: null,
      refetch: mockRefetch,
    })

    mockUseMutation.mockImplementation((mutation) => {
      if (mutation === CREATE_API_KEY) {
        return [
          (variables) => {
            mockCreateFn(variables)
            return Promise.resolve(mockCreateApiKeyResult)
          },
          { loading: false },
        ]
      }
      return [jest.fn(), { loading: false }]
    })

    render(<ApiKeysPage />)
    fireEvent.click(screen.getByText('Create New Key'))
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
    const nameInput = screen.getByLabelText('API Key Name')
    fireEvent.change(nameInput, { target: { value: 'Test Key' } })
    fireEvent.click(screen.getByRole('button', { name: /create api key/i }))
    await waitFor(() => {
      expect(mockCreateFn).toHaveBeenCalledWith({
        variables: { name: 'Test Key' },
      })
    })
  })

  test('handles API key revocation', async () => {
    const mockRevokeFn = jest.fn().mockRejectedValue(new Error('Revocation failed'))
    mockUseMutation.mockImplementation((mutation) => {
      if (mutation === REVOKE_API_KEY) {
        return [mockRevokeFn, { loading: false }]
      }
      return [jest.fn(), { loading: false }]
    })

    render(<ApiKeysPage />)
    const keyNameCell = await screen.findByText('mock key 1')
    const row = keyNameCell.closest('tr')
    const revokeButton = within(row).getByRole('button')
    fireEvent.click(revokeButton)
    const dialog = await screen.findByRole('dialog')
    expect(within(dialog).getByText('Revoke API Key')).toBeInTheDocument()
    expect(
      within(dialog).getByText(/Are you sure you want to revoke the key named/)
    ).toBeInTheDocument()
  })
})
