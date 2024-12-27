import { renderHook, act } from '@testing-library/react'

import { errorService } from 'lib/ErrorServeice'
import { useErrorHandler } from 'lib/hooks/useErrorHandler'

jest.mock('@sentry/react')
jest.mock('utils/logger', () => ({
  error: jest.fn(),
}))

describe('ErrorService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('handleError', () => {
    it('handles HTTP errors correctly', () => {
      const mockResponse = {
        status: 404,
        ok: false,
        statusText: 'Not Found',
      }
      const result = errorService.handleError(mockResponse)

      expect(result).toEqual({
        code: 'NOT_FOUND',
        statusCode: 404,
        title: 'Not Found',
        message: 'The requested resource could not be found.',
        source: 'http',
        action: 'home',
      })
    })

    it('handles server errors correctly', () => {
      const mockResponse = {
        status: 500,
        ok: false,
        statusText: 'Internal Server Error',
      }
      const result = errorService.handleError(mockResponse)

      expect(result).toEqual({
        code: 'SERVER_ERROR',
        statusCode: 500,
        title: 'Server Error',
        message: 'An unexpected server error occurred.',
        source: 'http',
        action: 'retry',
      })
    })

    it('handles search errors correctly', () => {
      const mockAlgoliaError = new Error('Algolia error')
      mockAlgoliaError.name = 'AlgoliaError'
      const result = errorService.handleError(mockAlgoliaError, 'search')

      expect(result).toEqual({
        code: 'ALGOLIA_SEARCH_FAILED',
        title: 'Search Error',
        message: 'Unable to complete search. Please try again.',
        source: 'algolia',
        action: 'retry',
      })
    })

    it('handles network errors', () => {
      const networkError = new Error('Failed to fetch')
      networkError.name = 'NetworkError'
      const result = errorService.handleError(networkError, 'network')

      expect(result).toEqual({
        code: 'NETWORK_ERROR',
        title: 'Connection Error',
        message: 'Please check your internet connection and try again.',
        source: 'network',
        action: 'retry',
      })
    })

    it('returns default error for unknown errors', () => {
      const result = errorService.handleError('unknown error')

      expect(result).toEqual({
        code: 'UNKNOWN_ERROR',
        title: 'Error',
        message: 'An unexpected error occurred.',
        source: 'runtime',
        action: 'home',
      })
    })
  })
})

describe('useErrorHandler', () => {
  const mockRetryFn = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    mockRetryFn.mockResolvedValue(undefined)
  })

  it('handles errors and sets error state', () => {
    const { result } = renderHook(() => useErrorHandler('search'))

    act(() => {
      result.current.handleError({
        status: 500,
        statusText: 'Internal Server Error',
      })
    })

    expect(result.current.error).toBeTruthy()
  })

  it('clears error state', () => {
    const { result } = renderHook(() => useErrorHandler())

    act(() => {
      result.current.handleError(new Error('Test error'))
    })

    act(() => {
      result.current.clearError()
    })

    expect(result.current.error).toBeNull()
  })

  it('handles retries up to maximum attempts', async () => {
    const { result } = renderHook(() => useErrorHandler())

    for (let i = 0; i < 4; i++) {
      await act(async () => {
        await result.current.retry(mockRetryFn)
      })
    }

    expect(result.current.error?.code).toBe('MAX_RETRIES_EXCEEDED')
    expect(mockRetryFn).toHaveBeenCalledTimes(3)
  })

  it('clears error on successful retry', async () => {
    const { result } = renderHook(() => useErrorHandler())

    act(() => {
      result.current.handleError(new Error('Test error'))
    })

    await act(async () => {
      await result.current.retry(mockRetryFn)
    })

    expect(result.current.error).toBeNull()
  })
})
