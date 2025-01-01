import * as Sentry from '@sentry/react'
import React from 'react'
import { useLocation } from 'react-router-dom'
import { ErrorDisplay, ERROR_CONFIGS } from 'lib/ErrorHandler'

export const ErrorWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation()

  return (
    <Sentry.ErrorBoundary
      fallback={() => <ErrorDisplay {...ERROR_CONFIGS['500']} />}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname)
        scope.setTag('environment', process.env.NODE_ENV)
      }}
    >
      {children}
    </Sentry.ErrorBoundary>
  )
}
