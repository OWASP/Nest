/* eslint-disable @typescript-eslint/naming-convention */
import { useQuery, useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
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

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}))

beforeAll(() => {
  jest.useFakeTimers()
  jest.setSystemTime(new Date('2025-12-04T00:00:00.000Z'))

  Object.defineProperty(navigator, 'clipboard', {
    value: { writeText: jest.fn().mockResolvedValue(undefined) },
    writable: true,
  })
})

afterAll(() => {
  jest.useRealTimers()
})

describe('ApiKeysPage Component', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseMutation = useMutation as unknown as jest.Mock
  const mockRefetch = jest.fn()
  const mockCreateMutation = jest.fn()
  const mockRevokeMutation = jest.fn()

  const createMutationFn = (
    mockFn: jest.Mock,
    options?: { onCompleted?: (data: unknown) => void }
  ) => {
    return jest.fn(async (vars) => {
      const result = await mockFn(vars)
      if (options?.onCompleted) {
        options.onCompleted(result.data)
      }
      return result
    })
  }

  const setupMocks = (overrides = {}) => {
    mockUseQuery.mockReturnValue({
      data: mockApiKeys,
      loading: false,
      error: null,
      refetch: mockRefetch,
      ...overrides,
    })

    mockUseMutation.mockImplementation((mutation, options) => {
      if (mutation === CreateApiKeyDocument) {
        return [createMutationFn(mockCreateMutation, options), { loading: false }]
      }
      if (mutation === RevokeApiKeyDocument) {
        return [createMutationFn(mockRevokeMutation, options), { loading: false }]
      }
      return [jest.fn(), { loading: false }]
    })

    mockCreateMutation.mockResolvedValue(mockCreateApiKeyResult)
    mockRevokeMutation.mockResolvedValue({ data: { revokeApiKey: { success: true } } })
  }

  const openCreateModal = async () => {
    fireEvent.click(screen.getByText(/Create New Key/))
    await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument())
  }

  const fillKeyForm = (name: string, expiry?: string) => {
    fireEvent.change(screen.getByLabelText('API Key Name'), { target: { value: name } })
    if (expiry) {
      fireEvent.change(screen.getByLabelText('Expiration Date'), { target: { value: expiry } })
    }
  }

  beforeEach(() => setupMocks())
  afterEach(() => jest.clearAllMocks())

  describe('Loading and Data States', () => {
    test('renders loading skeleton initially', () => {
      setupMocks({ data: null, loading: true })
      render(<ApiKeysPage />)
      expect(screen.queryByText('API Key Management')).not.toBeInTheDocument()
      // Note: Using direct DOM query as skeleton components don't have semantic roles
      expect(document.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)
    })

    test('displays API keys list when data is fetched', async () => {
      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText('mock key 1')).toBeInTheDocument()
        expect(screen.getByText('mock key 2')).toBeInTheDocument()
      })
    })

    test('displays empty state message when no API keys exist', async () => {
      setupMocks({ data: { apiKeys: [], activeApiKeyCount: 0 } })
      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText("You don't have any API keys yet.")).toBeInTheDocument()
      })
    })

    test('displays error message when query fails', async () => {
      setupMocks({ data: null, error: new Error('Failed to fetch') })
      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText('Error loading API keys')).toBeInTheDocument()
      })
    })
  })

  describe('API Key Creation', () => {
    test('creates API key with default 30-day expiry', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()
      fillKeyForm('Test New Key')
      fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

      const expectedDate = format(addDays(new Date(), 30), 'yyyy-MM-dd')
      const expectedIso = new Date(`${expectedDate}T00:00:00.000Z`).toISOString()

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith({
          variables: {
            name: 'Test New Key',
            expiresAt: expectedIso,
          },
        })
      })
    })

    test('creates API key with custom expiry date', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()
      fillKeyForm('Custom Expiry Key', '2025-12-31')
      fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith({
          variables: {
            name: 'Custom Expiry Key',
            expiresAt: new Date('2025-12-31T00:00:00.000Z').toISOString(),
          },
        })
      })
    })

    test('uses quick expiry buttons (90 days and 1 year)', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()

      fireEvent.click(screen.getByRole('button', { name: /90 days/i }))
      let expiryInput = screen.getByLabelText('Expiration Date') as HTMLInputElement
      expect(expiryInput.value).toBe(format(addDays(new Date(), 90), 'yyyy-MM-dd'))

      fireEvent.click(screen.getByRole('button', { name: /1 year/i }))
      expiryInput = screen.getByLabelText('Expiration Date') as HTMLInputElement
      expect(expiryInput.value).toBe(format(addDays(new Date(), 365), 'yyyy-MM-dd'))
    })
  })

  describe('Form Validation', () => {
    test('validates name length exceeds 100 characters', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()
      fillKeyForm('a'.repeat(101))
      fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Name must be less than 100 characters',
          color: 'danger',
        })
        expect(mockCreateMutation).not.toHaveBeenCalled()
      })
    })

    test('validates name contains only allowed characters', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()
      fillKeyForm('invalid@name!')
      fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Name can only contain letters, numbers, spaces, and hyphens',
          color: 'danger',
        })
        expect(mockCreateMutation).not.toHaveBeenCalled()
      })
    })

    test('validates expiration date is required', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()

      const expiryInput = screen.getByLabelText('Expiration Date') as HTMLInputElement
      fireEvent.change(expiryInput, { target: { value: '' } })
      fireEvent.change(screen.getByLabelText('API Key Name'), { target: { value: 'Valid Name' } })
      fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Please select an expiration date',
          color: 'danger',
        })
        expect(mockCreateMutation).not.toHaveBeenCalled()
      })
    })
  })

  describe('API Key Revocation', () => {
    test('revokes API key after confirmation', async () => {
      render(<ApiKeysPage />)
      const row = (await screen.findByText('mock key 1')).closest('tr')
      expect(row).not.toBeNull()
      fireEvent.click(within(row!).getByRole('button'))

      const dialog = await screen.findByRole('dialog')
      expect(within(dialog).getByText(/Are you sure you want to revoke/)).toBeInTheDocument()

      fireEvent.click(within(dialog).getByRole('button', { name: /Revoke Key/i }))
      await waitFor(() => {
        expect(mockRevokeMutation).toHaveBeenCalledWith({ variables: { uuid: '1' } })
      })
    })

    test('cancels revocation when cancel button is clicked', async () => {
      render(<ApiKeysPage />)
      const row = (await screen.findByText('mock key 1')).closest('tr')
      expect(row).not.toBeNull()
      fireEvent.click(within(row!).getByRole('button'))

      const dialog = await screen.findByRole('dialog')
      fireEvent.click(within(dialog).getByRole('button', { name: /Cancel/i }))

      await waitFor(() => {
        expect(mockRevokeMutation).not.toHaveBeenCalled()
      })
    })
  })

  describe('Key Limits and UI State', () => {
    test('disables create button and shows warning at maximum key limit', async () => {
      setupMocks({ data: { apiKeys: mockApiKeys.apiKeys, activeApiKeyCount: 3 } })
      render(<ApiKeysPage />)

      await waitFor(() => {
        expect(screen.getByText(/Create New Key/)).toBeDisabled()
        expect(
          screen.getByText(/You've reached the maximum number of API keys/)
        ).toBeInTheDocument()
      })
    })

    test('displays correct active key count', async () => {
      setupMocks({ data: { apiKeys: mockApiKeys.apiKeys, activeApiKeyCount: 2 } })
      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText(/2\s*\/\s*3\s*active keys/i)).toBeInTheDocument()
      })
    })

    test('displays API key usage information', async () => {
      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText('API Key Usage')).toBeInTheDocument()
        expect(screen.getByText('X-API-Key')).toBeInTheDocument()
        expect(screen.getByText(/Keep your API keys secure/)).toBeInTheDocument()
      })
    })
  })

  describe('Edge Cases', () => {
    test('disables create button when createLoading is true', async () => {
      const createLoadingMutation = (mutation: unknown, options?: unknown) => {
        if (mutation === CreateApiKeyDocument) {
          return [
            createMutationFn(
              mockCreateMutation,
              options as { onCompleted?: (data: unknown) => void }
            ),
            { loading: true },
          ]
        }
        if (mutation === RevokeApiKeyDocument) {
          return [
            createMutationFn(
              mockRevokeMutation,
              options as { onCompleted?: (data: unknown) => void }
            ),
            { loading: false },
          ]
        }
        return [jest.fn(), { loading: false }]
      }
      mockUseMutation.mockImplementation(createLoadingMutation)

      render(<ApiKeysPage />)
      await openCreateModal()
      fillKeyForm('Test Key')

      const createButton = screen.getByRole('button', { name: /create api key/i })
      expect(createButton).toBeDisabled()
    })

    test('cancels modal and resets state', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()
      fillKeyForm('Test Key', '2026-01-01')

      const cancelButton = screen.getByRole('button', { name: /Cancel/i })
      fireEvent.click(cancelButton)

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      })

      fireEvent.click(screen.getByText(/Create New Key/))
      await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument())

      const nameInput = screen.getByLabelText('API Key Name') as HTMLInputElement
      expect(nameInput.value).toBe('')
    })

    test('handles API keys with no expiration date', async () => {
      setupMocks({
        data: {
          apiKeys: [
            {
              uuid: '1',
              name: 'Never expires key',
              isRevoked: false,
              createdAt: '2025-07-11T08:17:45.406011+00:00',
              expiresAt: null,
            },
          ],
          activeApiKeyCount: 1,
        },
      })

      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText('Never expires key')).toBeInTheDocument()
        expect(screen.getByText('Never')).toBeInTheDocument()
      })
    })

    test('handles exactly 100 character name (boundary case)', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()

      const exactlyHundred = 'a'.repeat(100)
      fillKeyForm(exactlyHundred)
      fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith({
          variables: expect.objectContaining({
            name: exactlyHundred,
          }),
        })
      })
    })

    test('displays button text with correct active key count', async () => {
      setupMocks({ data: { apiKeys: mockApiKeys.apiKeys, activeApiKeyCount: 1 } })
      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText(/Create New Key \(1\/3\)/)).toBeInTheDocument()
      })
    })

    test('accepts valid name with hyphens and spaces', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()

      const validName = 'My API Key-123'
      fillKeyForm(validName)
      fireEvent.click(screen.getByRole('button', { name: /create api key/i }))

      await waitFor(() => {
        expect(mockCreateMutation).toHaveBeenCalledWith({
          variables: expect.objectContaining({
            name: validName,
          }),
        })
      })
    })

    test('displays multiple keys in table correctly', async () => {
      setupMocks({
        data: {
          apiKeys: [
            ...mockApiKeys.apiKeys,
            {
              uuid: '3',
              name: 'third key',
              isRevoked: false,
              createdAt: '2025-07-10T08:17:45.406011+00:00',
              expiresAt: '2025-12-31T00:00:00+00:00',
            },
          ],
          activeApiKeyCount: 3,
        },
      })

      render(<ApiKeysPage />)
      await waitFor(() => {
        expect(screen.getByText('mock key 1')).toBeInTheDocument()
        expect(screen.getByText('mock key 2')).toBeInTheDocument()
        expect(screen.getByText('third key')).toBeInTheDocument()
      })
    })

    test('displays table with date columns', async () => {
      render(<ApiKeysPage />)
      await waitFor(() => {
        const table = screen.getByRole('table')
        expect(table).toBeInTheDocument()
        expect(screen.getByText('Created')).toBeInTheDocument()
        expect(screen.getByText('Expires')).toBeInTheDocument()
      })
    })

    test('disables create button when name input is empty', async () => {
      render(<ApiKeysPage />)
      await openCreateModal()

      const createButton = screen.getByRole('button', { name: /create api key/i })
      expect(createButton).toBeDisabled()
    })
  })
})
