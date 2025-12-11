import { addToast } from '@heroui/toast'
import * as Sentry from '@sentry/nextjs'
import { screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import GlobalError, {
  AppError,
  ERROR_CONFIGS,
  ErrorDisplay,
  ErrorWrapper,
  handleAppError,
} from 'app/global-error'

// Mocks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))
jest.mock('@sentry/nextjs', () => ({
  captureException: jest.fn(),
  ErrorBoundary: ({ _fallback, children }) => <>{children}</>,
}))
jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

describe('ErrorDisplay Component', () => {
  test('renders correct error details', () => {
    render(<ErrorDisplay statusCode={404} title="Not Found" message="Page not found" />)

    expect(screen.getByText('404')).toBeInTheDocument()
    expect(screen.getByText('Not Found')).toBeInTheDocument()
    expect(screen.getByText('Page not found')).toBeInTheDocument()
  })

  test('navigates to home on button press', () => {
    const pushMock = jest.fn()
    ;(useRouter as jest.Mock).mockReturnValue({ push: pushMock })

    render(<ErrorDisplay {...ERROR_CONFIGS['404']} />)

    fireEvent.click(screen.getByText('Return To Home'))
    expect(pushMock).toHaveBeenCalledWith('/')
  })
})

describe('handleAppError Function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('handles AppError without Sentry for 404', () => {
    const error = new AppError(404, 'Page not found')
    handleAppError(error)

    expect(Sentry.captureException).not.toHaveBeenCalled()
    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Page Not Found',
        description: 'Page not found',
      })
    )
  })

  test('handles unknown error and calls Sentry for 500+', () => {
    handleAppError('Unknown crash')

    expect(Sentry.captureException).toHaveBeenCalled()
    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        description: 'An unexpected server error occurred.',
        shouldShowTimeoutProgress: true,
        timeout: 5000,
        title: 'Server Error',
      })
    )
  })

  test('handles normal Error instance', () => {
    const err = new Error('Oops')
    handleAppError(err)

    expect(Sentry.captureException).toHaveBeenCalledWith(err)
    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        description: 'Oops',
      })
    )
  })
})

describe('AppError class', () => {
  test('should extend Error properly', () => {
    const err = new AppError(403, 'Forbidden')
    expect(err).toBeInstanceOf(Error)
    expect(err.name).toBe('AppError')
    expect(err.message).toBe('Forbidden')
    expect(err.statusCode).toBe(403)
  })
})

describe('GlobalError component', () => {
  test('renders 500 fallback and calls Sentry', () => {
    const error = new Error('Critical failure')
    render(<GlobalError error={error} />)

    expect(Sentry.captureException).toHaveBeenCalledWith(error)
    expect(screen.getByText('Server Error')).toBeInTheDocument()
    const button = screen.getByRole('button', { name: 'Return to Home' })
    expect(button).toHaveClass(
      'bg-owasp-blue',
      'dark:bg-slate-800'
    )
  })
})

describe('ErrorWrapper component', () => {
  test('renders children without crashing', () => {
    render(
      <ErrorWrapper>
        <div>App Content</div>
      </ErrorWrapper>
    )

    expect(screen.getByText('App Content')).toBeInTheDocument()
  })
})
