import * as Sentry from '@sentry/react'
import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { toast } from 'lib/hooks/use-toast'

interface ErrorDisplayProps {
  statusCode: number
  title: string
  message: string
}

export const ERROR_CONFIGS: Record<string, ErrorDisplayProps> = {
  '404': {
    statusCode: 404,
    title: 'Page Not Found',
    message: "The page you're looking for doesn't exist.",
  },
  '500': {
    statusCode: 500,
    title: 'Server Error',
    message: 'An unexpected server error occurred.',
  },
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ statusCode, title, message }) => {
  const navigate = useNavigate()
  return (
    <main className="flex min-h-screen flex-col items-center bg-white pt-8 dark:bg-slate-900">
      <div className="flex flex-1 flex-col items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <h1 className="font-poppins text-8xl font-semibold text-black dark:text-white">
            {statusCode}
          </h1>
          <h2 className="font-inter mt-4 text-2xl font-semibold text-black dark:text-white">
            {title}
          </h2>
          <p className="font-inter mt-2 text-lg text-black dark:text-white">{message}</p>
          <button
            onClick={() => navigate('/')}
            className="font-inter mt-8 h-12 w-40 rounded-lg bg-owasp-blue text-base font-medium text-white transition-colors hover:bg-blue-400"
          >
            Return To Home
          </button>
        </div>
      </div>
    </main>
  )
}

export class AppError extends Error {
  constructor(
    public statusCode = 500,
    message = 'Something went wrong'
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export const handleAppError = (error: unknown): void => {
  Sentry.captureException(error)

  if (error instanceof AppError && error.statusCode === 404) {
    throw error
  }

  // Show toast for all other errors
  toast({
    variant: 'destructive',
    title: 'Error',
    description: 'Something went wrong',
  })
}

export const ErrorWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation()

  return (
    <Sentry.ErrorBoundary
      fallback={({ error }) => {
        if (error instanceof AppError && error.statusCode === 404) {
          return <ErrorDisplay {...ERROR_CONFIGS['404']} />
        }
        return <ErrorDisplay {...ERROR_CONFIGS['500']} />
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
