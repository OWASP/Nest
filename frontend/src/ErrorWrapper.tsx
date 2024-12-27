import * as Sentry from '@sentry/react'
import React from 'react'
import { useLocation } from 'react-router-dom'

import { errorService } from 'lib/ErrorServeice'
import { ErrorDisplay } from 'components/ErrorDisplay'

interface Props {
  children: React.ReactNode
}

const ErrorWrapper: React.FC<Props> = ({ children }) => {
  const location = useLocation()

  return (
    <Sentry.ErrorBoundary
      fallback={({ error }) => {
        const errorConfig = errorService.handleError(error, 'boundary')
        return <ErrorDisplay error={errorConfig} />
      }}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname)
        scope.setTag('environment', process.env.NODE_ENV)
      }}
    >
      {children}
    </Sentry.ErrorBoundary>
  )
}
export default ErrorWrapper
