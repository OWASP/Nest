import { useQuery } from '@apollo/client/react'
import { mockApiKeys } from '@mockData/mockApiKeysData'
import { screen, fireEvent, waitFor, within } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import ApiKeysPage from 'app/settings/api-keys/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(() => [jest.fn(), { loading: false }]),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

describe('ApiKeysPage Accessibility', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock

  it('should have no violations in default data-loaded state', async () => {
    mockUseQuery.mockReturnValue({ data: mockApiKeys, loading: false, error: false })

    const { container } = render(<ApiKeysPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations in loading state', async () => {
    mockUseQuery.mockReturnValue({ data: null, loading: true })
    const { container } = render(<ApiKeysPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations in empty state', async () => {
    mockUseQuery.mockReturnValue({ data: { apiKeys: [], activeApiKeyCount: 0 }, loading: false })
    const { container } = render(<ApiKeysPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations when Create Modal is open', async () => {
    mockUseQuery.mockReturnValue({ data: mockApiKeys, loading: false })

    const { container } = render(<ApiKeysPage />)

    const openButton = screen.getByText(/Create New Key/i)
    fireEvent.click(openButton)

    await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument())

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations when Revoke Confirmation is open', async () => {
    mockUseQuery.mockReturnValue({ data: mockApiKeys, loading: false })

    const { container } = render(<ApiKeysPage />)

    const row = (await screen.findByText('mock key 1')).closest('tr')!
    fireEvent.click(within(row).getByRole('button'))

    await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument())

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
