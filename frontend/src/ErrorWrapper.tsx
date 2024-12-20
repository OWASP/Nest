import * as Sentry from '@sentry/react'
import React from 'react'

import ErrorMessage from './components/ErrorMessage'

interface CustomError extends Error {
  statusCode?: number
}

const ErrorWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Sentry.ErrorBoundary
    fallback={({ error }) => {
      const typedError = error as CustomError
      const statusCode = typedError?.statusCode || undefined
      const message =
        statusCode === 404
          ? 'Page not found.'
          : statusCode
            ? `An unexpected error occurred (Code: ${statusCode}).`
            : 'A runtime error occurred. Please try again later.'

      return <ErrorMessage message={message} statusCode={statusCode} />
    }}
  >
    {children}
  </Sentry.ErrorBoundary>
)

export default ErrorWrapper
