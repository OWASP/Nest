import { ChakraProvider, defaultSystem } from '@chakra-ui/react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { postFeedback } from 'api/postFeedbackData'
import FeedbackPage from 'pages/Feedback'

// Mock ReCAPTCHA
jest.mock('react-google-recaptcha', () => ({
  __esModule: true,
  default: jest.fn(({ onChange }) => (
    <button data-testid="recaptcha-button" onClick={() => onChange && onChange('test-token')}>
      Verify ReCAPTCHA
    </button>
  )),
}))

// Mock postFeedback API
jest.mock('api/postFeedbackData')
const mockPostFeedback = postFeedback as jest.Mock

describe('FeedbackPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders FeedbackPage with FeedbackForm', () => {
    render(
      <ChakraProvider value={defaultSystem}>
        <ChakraProvider value={defaultSystem}>
          <FeedbackPage />
        </ChakraProvider>
      </ChakraProvider>
    )

    expect(screen.getByText('Feedback form')).toBeInTheDocument()
  })

  test('submits feedback successfully', async () => {
    mockPostFeedback.mockResolvedValueOnce({ ok: true })

    render(
      <ChakraProvider value={defaultSystem}>
        <ChakraProvider value={defaultSystem}>
          <FeedbackPage />
        </ChakraProvider>
      </ChakraProvider>
    )

    fireEvent.change(screen.getByPlaceholderText('Your name'), {
      target: { value: 'John Doe' },
    })
    fireEvent.change(screen.getByPlaceholderText('email@example.com'), {
      target: { value: 'john@example.com' },
    })
    fireEvent.change(screen.getByPlaceholderText('Your feedback here...'), {
      target: { value: 'Great job!' },
    })

    fireEvent.click(screen.getByTestId('recaptcha-button'))

    fireEvent.click(screen.getByRole('button', { name: /submit feedback/i }))

    await waitFor(() => {
      expect(mockPostFeedback).toHaveBeenCalledTimes(0)
    })

    expect(screen.getByText('Submitting...')).toBeInTheDocument()
  })

  test('shows error when feedback submission fails', async () => {
    mockPostFeedback.mockResolvedValueOnce({ ok: false })

    render(
      <ChakraProvider value={defaultSystem}>
        <ChakraProvider value={defaultSystem}>
          <FeedbackPage />
        </ChakraProvider>
      </ChakraProvider>
    )

    fireEvent.change(screen.getByPlaceholderText('Your name'), {
      target: { value: 'John Doe' },
    })
    fireEvent.change(screen.getByPlaceholderText('email@example.com'), {
      target: { value: 'john@example.com' },
    })
    fireEvent.change(screen.getByPlaceholderText('Your feedback here...'), {
      target: { value: 'Great job!' },
    })

    fireEvent.click(screen.getByTestId('recaptcha-button'))

    fireEvent.click(screen.getByRole('button', { name: /submit feedback/i }))

    await waitFor(() => {
      expect(screen.getByText('Anonymous Feedback')).toBeInTheDocument()
    })
  })

  test('shows error when submitting without verifying ReCAPTCHA', async () => {
    render(
      <ChakraProvider value={defaultSystem}>
        <ChakraProvider value={defaultSystem}>
          <FeedbackPage />
        </ChakraProvider>
      </ChakraProvider>
    )

    fireEvent.change(screen.getByPlaceholderText('Your name'), {
      target: { value: 'John Doe' },
    })
    fireEvent.change(screen.getByPlaceholderText('email@example.com'), {
      target: { value: 'john@example.com' },
    })
    fireEvent.change(screen.getByPlaceholderText('Your feedback here...'), {
      target: { value: 'Great job!' },
    })

    fireEvent.click(screen.getByRole('button', { name: /submit feedback/i }))

    await waitFor(() => {
      expect(screen.getByText('Please complete the reCAPTCHA.')).toBeInTheDocument()
    })
  })

  test('toggles anonymous feedback mode', async () => {
    render(
      <ChakraProvider value={defaultSystem}>
        <ChakraProvider value={defaultSystem}>
          <FeedbackPage />
        </ChakraProvider>
      </ChakraProvider>
    )

    fireEvent.click(screen.getByRole('checkbox', { name: /anonymous feedback/i }))

    await waitFor(() => {
      expect(screen.queryByPlaceholderText('Your name')).not.toBeInTheDocument()
      expect(screen.queryByPlaceholderText('email@example.com')).not.toBeInTheDocument()
    })
  })

  test('resets form after successful submission', async () => {
    mockPostFeedback.mockResolvedValueOnce({ ok: true })

    render(
      <ChakraProvider value={defaultSystem}>
        <ChakraProvider value={defaultSystem}>
          <FeedbackPage />
        </ChakraProvider>
      </ChakraProvider>
    )

    fireEvent.change(screen.getByPlaceholderText('Your name'), {
      target: { value: 'John Doe' },
    })
    fireEvent.change(screen.getByPlaceholderText('email@example.com'), {
      target: { value: 'john@example.com' },
    })
    fireEvent.change(screen.getByPlaceholderText('Your feedback here...'), {
      target: { value: 'Great job!' },
    })

    fireEvent.click(screen.getByTestId('recaptcha-button'))

    fireEvent.click(screen.getByRole('button', { name: /submit feedback/i }))

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Your name')).toHaveValue('John Doe')
      expect(screen.getByPlaceholderText('email@example.com')).toHaveValue('john@example.com')
      expect(screen.getByPlaceholderText('Your feedback here...')).toHaveValue('Great job!')
    })
  })
})
