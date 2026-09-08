import { useMutation } from '@apollo/client/react'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import UnsubscribePage from 'app/unsubscribe/[token]/page'

jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ token: 'test-token-123' }),
}))

describe('UnsubscribePage', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders loading state initially', () => {
    const mockUnsubscribe = jest.fn().mockReturnValue(new Promise(() => {}))
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])

    render(<UnsubscribePage />)

    const loadingSpinner = screen.getAllByAltText('Loading indicator')
    expect(loadingSpinner.length).toBeGreaterThan(0)
  })

  test('renders success state after successful unsubscribe', async () => {
    const mockUnsubscribe = jest.fn().mockResolvedValue({
      data: {
        unsubscribeByToken: {
          ok: true,
          message: 'Unsubscribed successfully',
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByText('Unsubscribed')).toBeInTheDocument()
    })

    expect(screen.getByText('You have been successfully unsubscribed.')).toBeInTheDocument()
    expect(
      screen.getByText('You will no longer receive snapshot digest emails for this subscription.')
    ).toBeInTheDocument()
    expect(screen.getByText('Return To Home')).toBeInTheDocument()
  })

  test('renders error state when unsubscribe fails with message', async () => {
    const mockUnsubscribe = jest.fn().mockResolvedValue({
      data: {
        unsubscribeByToken: {
          ok: false,
          message: 'Invalid or expired token',
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Invalid or expired token')).toBeInTheDocument()
  })

  test('renders error state when mutation throws', async () => {
    const mockUnsubscribe = jest.fn().mockRejectedValue(new Error('Network error'))
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Something went wrong. Please try again later.')).toBeInTheDocument()
  })

  test('renders fallback error message when no message provided', async () => {
    const mockUnsubscribe = jest.fn().mockResolvedValue({
      data: {
        unsubscribeByToken: {
          ok: false,
          message: '',
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByText('Unsubscribe Failed')).toBeInTheDocument()
    })

    expect(screen.getByText('Failed to unsubscribe.')).toBeInTheDocument()
  })

  test('calls unsubscribe mutation with token', async () => {
    const mockUnsubscribe = jest.fn().mockResolvedValue({
      data: {
        unsubscribeByToken: {
          ok: true,
          message: 'Done',
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(mockUnsubscribe).toHaveBeenCalledWith({
        variables: { token: 'test-token-123' },
      })
    })
  })

  test('navigates to home when Return To Home button is clicked', async () => {
    const mockUnsubscribe = jest.fn().mockResolvedValue({
      data: {
        unsubscribeByToken: {
          ok: true,
          message: 'Done',
        },
      },
    })
    ;(useMutation as unknown as jest.Mock).mockReturnValue([mockUnsubscribe])

    render(<UnsubscribePage />)

    await waitFor(() => {
      expect(screen.getByText('Unsubscribed')).toBeInTheDocument()
    })

    const homeButton = screen.getByRole('button', { name: /return to home/i })
    fireEvent.click(homeButton)

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/')
    })
  })
})
