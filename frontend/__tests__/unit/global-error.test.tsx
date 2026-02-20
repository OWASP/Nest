import { addToast } from '@heroui/toast'
import * as Sentry from '@sentry/nextjs'
import { screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'
import { render } from 'wrappers/testUtil'
import GlobalError, {
  AppError,
  ERROR_CONFIGS,
  ErrorDisplay,
  ErrorWrapper,
  handleAppError,
  SentryErrorFallback,
} from 'app/global-error'

// Mocks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Create a custom ErrorBoundary mock that can trigger fallback
let shouldThrowError = false
jest.mock('@sentry/nextjs', () => ({
  captureException: jest.fn(),
  ErrorBoundary: ({
    fallback,
    children,
  }: {
    fallback?: (errorInfo: { error: Error }) => React.ReactNode
    children: React.ReactNode
  }) => {
    if (shouldThrowError && typeof fallback === 'function') {
      return fallback({ error: new Error('Boundary test error') })
    }
    return <>{children}</>
  },
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

  test('renders 500 error display correctly', () => {
    render(<ErrorDisplay {...ERROR_CONFIGS['500']} />)

    expect(screen.getByText('500')).toBeInTheDocument()
    expect(screen.getByText('Server Error')).toBeInTheDocument()
    expect(screen.getByText('An unexpected server error occurred.')).toBeInTheDocument()
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

  test('uses 404 config for AppError with 404 status code', () => {
    const error = new AppError(404, 'Custom 404 message')
    handleAppError(error)

    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: ERROR_CONFIGS['404'].title,
      })
    )
  })

  test('uses 500 config for AppError with 500 status code', () => {
    const error = new AppError(500, 'Server error')
    handleAppError(error)

    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: ERROR_CONFIGS['500'].title,
      })
    )
  })

  test('handles unknown error and calls Sentry for 500+', () => {
    handleAppError('Unknown crash')

    expect(Sentry.captureException).toHaveBeenCalled()
    const captureCall = (Sentry.captureException as jest.Mock).mock.calls[0][0]
    expect(captureCall).toBeInstanceOf(AppError)
    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        description: 'An unexpected server error occurred.',
        shouldShowTimeoutProgress: true,
        timeout: 5000,
        title: 'Server Error',
      })
    )
  })

  test('uses error message when available, falls back to config message', () => {
    const error = new AppError(404, '')
    handleAppError(error)

    expect(addToast).toHaveBeenCalledWith(
      expect.objectContaining({
        description: ERROR_CONFIGS['404'].message,
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

  test('should use default values when no arguments provided', () => {
    const err = new AppError()
    expect(err.statusCode).toBe(500)
    expect(err.message).toBe('Something went wrong')
    expect(err.name).toBe('AppError')
  })

  test('should handle all statusCode values', () => {
    const err404 = new AppError(404, 'Not found')
    const err500 = new AppError(500, 'Server error')

    expect(err404.statusCode).toBe(404)
    expect(err500.statusCode).toBe(500)
  })

  test('should handle when Error.captureStackTrace is not available', () => {
    const originalCaptureStackTrace = Error.captureStackTrace
    delete (Error as unknown as { captureStackTrace?: unknown }).captureStackTrace

    const err = new AppError(500, 'Test')
    expect(err.name).toBe('AppError')
    expect(err.statusCode).toBe(500)
    ;(Error as unknown as { captureStackTrace?: unknown }).captureStackTrace =
      originalCaptureStackTrace
  })
})

describe('GlobalError component', () => {
  test('renders 500 fallback and calls Sentry', () => {
    const error = new Error('Critical failure')
    render(<GlobalError error={error} />)

    expect(Sentry.captureException).toHaveBeenCalledWith(error)
    expect(screen.getByText('Server Error')).toBeInTheDocument()
    const button = screen.getByRole('button', { name: 'Return to Home' })
    expect(button).toHaveClass('bg-owasp-blue', 'dark:bg-slate-800')
  })
})

describe('ErrorWrapper component', () => {
  test('renders children without crashing', () => {
    shouldThrowError = false
    render(
      <ErrorWrapper>
        <div>App Content</div>
      </ErrorWrapper>
    )

    expect(screen.getByText('App Content')).toBeInTheDocument()
  })

  test('renders error display fallback on boundary error', () => {
    shouldThrowError = true
    render(
      <ErrorWrapper>
        <div>App Content</div>
      </ErrorWrapper>
    )

    expect(Sentry.captureException).toHaveBeenCalled()
    expect(screen.getByText('500')).toBeInTheDocument()
    expect(screen.getByText('Server Error')).toBeInTheDocument()

    shouldThrowError = false
  })
})

describe('SentryErrorFallback component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('captures exception and renders default 500 error display', () => {
    const error = new Error('Boundary caught error')
    render(<SentryErrorFallback error={error} />)

    expect(Sentry.captureException).toHaveBeenCalledWith(error)
    expect(screen.getByText('500')).toBeInTheDocument()
    expect(screen.getByText('Server Error')).toBeInTheDocument()
  })

  test('uses custom errorConfig when provided', () => {
    const error = new Error('Custom error')
    const customConfig = { statusCode: 404, title: 'Custom Not Found', message: 'Custom message' }
    render(<SentryErrorFallback error={error} errorConfig={customConfig} />)

    expect(Sentry.captureException).toHaveBeenCalledWith(error)
    expect(screen.getByText('404')).toBeInTheDocument()
    expect(screen.getByText('Custom Not Found')).toBeInTheDocument()
    expect(screen.getByText('Custom message')).toBeInTheDocument()
  })
})
