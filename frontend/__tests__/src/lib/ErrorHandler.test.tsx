import * as Sentry from '@sentry/react'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ErrorDisplay, handleError, ERROR_CONFIGS } from 'lib/ErrorHandler' // Adjust the path as necessary
import { toast } from 'lib/hooks/use-toast'

jest.mock('@sentry/react', () => ({
  captureException: jest.fn(),
}))

jest.mock('lib/hooks/use-toast', () => ({
  toast: jest.fn(),
}))

const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}))

describe('ErrorHandler Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  // Test cases for ErrorDisplay
  describe('ErrorDisplay Component', () => {
    it('renders the correct status code, title, and message', () => {
      render(
        <MemoryRouter>
          <ErrorDisplay
            statusCode={404}
            title="Page Not Found"
            message="The page you're looking for doesn't exist."
          />
        </MemoryRouter>
      )

      expect(screen.getByRole('heading', { level: 1, name: '404' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { level: 2, name: 'Page Not Found' })).toBeInTheDocument()
      expect(screen.getByText("The page you're looking for doesn't exist.")).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Return To Home' })).toBeInTheDocument()
    })

    it('navigates to home when the button is clicked', () => {
      render(
        <MemoryRouter>
          <ErrorDisplay
            statusCode={404}
            title="Page Not Found"
            message="The page you're looking for doesn't exist."
          />
        </MemoryRouter>
      )

      const button = screen.getByRole('button', { name: 'Return To Home' })
      fireEvent.click(button)

      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  // Test cases for handleError
  describe('handleError Function', () => {
    it('logs NotFoundError and returns the 404 ErrorDisplay component', () => {
      const error = new Error()
      error.name = 'NotFoundError'

      const result = handleError(error, mockNavigate)

      expect(result).not.toBeUndefined()
      if (!result) {
        throw new Error('Expected result to be a React element')
      }

      render(<MemoryRouter>{result}</MemoryRouter>)

      expect(screen.getByRole('heading', { level: 1, name: '404' })).toBeInTheDocument()
      expect(
        screen.getByRole('heading', { level: 2, name: ERROR_CONFIGS['404'].title })
      ).toBeInTheDocument()
      expect(screen.getByText(ERROR_CONFIGS['404'].message)).toBeInTheDocument()

      expect(Sentry.captureException).toHaveBeenCalledWith(error)
      expect(toast).not.toHaveBeenCalled()
    })

    it('logs ServerError and returns the 500 ErrorDisplay component', () => {
      const error = new Error()
      error.name = 'ServerError'

      const result = handleError(error, mockNavigate)

      expect(result).not.toBeUndefined()
      if (!result) {
        throw new Error('Expected result to be a React element')
      }

      render(<MemoryRouter>{result}</MemoryRouter>)

      expect(screen.getByText(ERROR_CONFIGS['500'].statusCode.toString())).toBeInTheDocument()
      expect(screen.getByText(ERROR_CONFIGS['500'].title)).toBeInTheDocument()
      expect(screen.getByText(ERROR_CONFIGS['500'].message)).toBeInTheDocument()

      expect(Sentry.captureException).toHaveBeenCalledWith(error)
      expect(toast).not.toHaveBeenCalled()
    })

    it('shows toast error for other error types and navigates to home', () => {
      const error = new Error('Some other error')

      const result = handleError(error, mockNavigate)

      expect(result).toBeUndefined()
      expect(toast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Error',
        description: 'Something went wrong',
      })
      expect(mockNavigate).toHaveBeenCalledWith('/')
      expect(Sentry.captureException).toHaveBeenCalledWith(error)
    })

    it('shows toast error and navigates for non-error objects', () => {
      const error = 'Non-error object'

      const result = handleError(error, mockNavigate)

      expect(result).toBeUndefined()
      expect(toast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Error',
        description: 'Something went wrong',
      })
      expect(mockNavigate).toHaveBeenCalledWith('/')
      expect(Sentry.captureException).toHaveBeenCalledWith(error)
    })
  })
})
