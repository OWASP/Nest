import { useState, useCallback } from 'react'

import { errorService } from 'lib/ErrorServeice'
import type { ErrorConfig } from 'lib/types'

export const useErrorHandler = (context?: string) => {
  const [error, setError] = useState<ErrorConfig | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const MAX_RETRIES = 3

  const handleError = useCallback(
    (error: unknown) => {
      const errorConfig = errorService.handleError(error, context)
      setError(errorConfig)
    },
    [context]
  )

  const clearError = () => {
    setError(null)
    setRetryCount(0)
  }

  const retry = useCallback(
    async (retryFn: () => Promise<void>) => {
      if (retryCount >= MAX_RETRIES) {
        const errorConfig = {
          code: 'MAX_RETRIES_EXCEEDED',
          title: 'Too Many Attempts',
          message: 'Please try again later or return home.',
          source: 'runtime' as const,
          action: 'home' as const,
        }
        setError(errorConfig)
        return
      }

      setRetryCount((prev) => prev + 1)
      setError(null)

      try {
        await retryFn()
      } catch (error) {
        handleError(error)
      }
    },
    [retryCount, handleError]
  )

  return { error, handleError, clearError, retry }
}
