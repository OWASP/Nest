import { useLazyQuery, useMutation } from '@apollo/client/react'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import UnsubscribePage from 'app/unsubscribe/[token]/page'

jest.mock('@apollo/client/react', () => ({
  useLazyQuery: jest.fn(),
  useMutation: jest.fn(),
}))

const mockRegisterBreadcrumb = jest.fn()
jest.mock('contexts/BreadcrumbContext', () => ({
  ...jest.requireActual('contexts/BreadcrumbContext'),
  registerBreadcrumb: (...args: [{ title: string; path: string }]) =>
    mockRegisterBreadcrumb(...args),
}))

const mockRouter = {
  push: jest.fn(),
}

const mockUseParams = jest.fn(() => ({ token: 'test-token-123' }))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => mockUseParams(),
}))

describe('UnsubscribePage', () => {
  let mockFetchSubscription: jest.Mock
  let mockUnsubscribe: jest.Mock

  beforeEach(() => {
    mockFetchSubscription = jest.fn()
    mockUnsubscribe = jest.fn()
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([mockFetchSubscription])
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state while fetching subscription info', () => {
    mockFetchSubscription.mockReturnValue(new Promise(() => {}))

    render(<UnsubscribePage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    expect(loadingSpinner.length).toBeGreaterThan(0)
  })

  test('renders confirmation screen with subscription name', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    expect(screen.getByText('My Weekly Digest')).toBeInTheDocument()
    expect(screen.getByText(/Are you sure you want to unsubscribe from/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
  })

  test('calls unsubscribe mutation when Confirm is clicked', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })
    mockUnsubscribe.mockResolvedValue({
      data: { unsubscribeByToken: { ok: true, message: 'Done' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /confirm unsubscribe/i }))

    await waitFor(() => {
      expect(mockUnsubscribe).toHaveBeenCalledWith({
        variables: { inputData: { token: 'test-token-123' } },
      })
    })
  })

  test('renders success state with subscription name after confirming', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })
    mockUnsubscribe.mockResolvedValue({
      data: { unsubscribeByToken: { ok: true, message: 'Done' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /confirm unsubscribe/i }))

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /unsubscribed/i })).toBeInTheDocument()
    })

    expect(screen.getByText('My Weekly Digest')).toBeInTheDocument()
    expect(screen.getByText(/You have been unsubscribed from/)).toBeInTheDocument()
    expect(screen.getByText('Return To Home')).toBeInTheDocument()
  })

  test('renders error when token is invalid (query returns null)', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: null },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Invalid or expired unsubscribe link.')).toBeInTheDocument()
  })

  test('renders error when subscription query throws', async () => {
    mockFetchSubscription.mockRejectedValue(new Error('Network error'))

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Something went wrong. Please try again later.')).toBeInTheDocument()
  })

  test('renders error when mutation fails with message', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })
    mockUnsubscribe.mockResolvedValue({
      data: { unsubscribeByToken: { ok: false, message: 'Token already used' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /confirm unsubscribe/i }))

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Token already used')).toBeInTheDocument()
  })

  test('renders fallback error when mutation fails without message', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })
    mockUnsubscribe.mockResolvedValue({
      data: { unsubscribeByToken: { ok: false, message: '' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /confirm unsubscribe/i }))

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Failed to unsubscribe.')).toBeInTheDocument()
  })

  test('renders error when mutation throws', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })
    mockUnsubscribe.mockRejectedValue(new Error('Network error'))

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /confirm unsubscribe/i }))

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Something went wrong. Please try again later.')).toBeInTheDocument()
  })

  test('navigates to home when Cancel is clicked', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /cancel/i }))

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/')
    })
  })

  test('navigates to home when Return To Home is clicked after success', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })
    mockUnsubscribe.mockResolvedValue({
      data: { unsubscribeByToken: { ok: true, message: 'Done' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /confirm unsubscribe/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /confirm unsubscribe/i }))

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /unsubscribed/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /return to home/i }))

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/')
    })
  })

  test('fetches subscription info with correct token', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'Test Sub' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(mockFetchSubscription).toHaveBeenCalledWith({
        variables: { token: 'test-token-123' },
      })
      expect(mockFetchSubscription).toHaveBeenCalledTimes(1)
    })
  })

  test('registers breadcrumb with subscription name after fetch', async () => {
    mockFetchSubscription.mockResolvedValue({
      data: { subscriptionByToken: { name: 'My Weekly Digest' } },
    })

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(mockRegisterBreadcrumb).toHaveBeenCalledWith({
        title: 'My Weekly Digest',
        path: '/unsubscribe/test-token-123',
      })
    })
  })

  test('does not register breadcrumb when subscription name is empty', () => {
    mockFetchSubscription.mockReturnValue(new Promise(() => {}))

    render(<UnsubscribePage />)

    expect(mockRegisterBreadcrumb).not.toHaveBeenCalled()
  })
})
