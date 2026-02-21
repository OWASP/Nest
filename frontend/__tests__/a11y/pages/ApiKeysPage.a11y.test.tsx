import { useQuery } from '@apollo/client/react'
import { mockApiKeys } from '@mockData/mockApiKeysData'
import { screen, fireEvent, waitFor, within } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ApiKeysPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
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
    // Suppress jsdom TreeWalker limitation with @react-aria/focus FocusScope
    jest.spyOn(console, 'error').mockImplementation((...args) => {
      if (typeof args[0] === 'string' && args[0].includes('TreeWalker')) return
      throw new Error(`Console error: ${args.join(' ')}`)
    })
    mockUseQuery.mockReturnValue({ data: mockApiKeys, loading: false })

    const { container } = render(<ApiKeysPage />)

    const row = (await screen.findByText('mock key 1')).closest('tr')!
    fireEvent.click(within(row).getByRole('button'))

    await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument())

    const results = await axe(container)
    expect(results).toHaveNoViolations()
    jest.restoreAllMocks()
  })
})
