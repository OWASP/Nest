import { Button } from '@chakra-ui/react'
import * as Sentry from '@sentry/react'
import { toast } from 'hooks/useToast'
import React from 'react'
import { useNavigate } from 'react-router-dom'

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
          <Button
            onClick={() => navigate('/')}
            className="font-inter mt-8 h-12 w-40 rounded-lg bg-owasp-blue text-base font-medium text-white transition-colors hover:bg-blue-400"
          >
            Return To Home
          </Button>
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
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AppError)
    }
  }
}

export const handleAppError = (error: unknown) => {
  const appError =
    error instanceof AppError
      ? error
      : new AppError(500, error instanceof Error ? error.message : ERROR_CONFIGS['500'].message)

  // Log to Sentry
  if (appError.statusCode >= 500) {
    Sentry.captureException(error instanceof Error ? error : appError)
  }
  const errorConfig = ERROR_CONFIGS[appError.statusCode === 404 ? '404' : '500']

  toast({
    variant: 'destructive',
    title: errorConfig.title,
    description: errorConfig.message || appError.message,
    duration: 5000,
  })
}

// Main error boundary wrapper
export const ErrorWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Sentry.ErrorBoundary
      fallback={({ error }) => {
        Sentry.captureException(error)
        const errorConfig = ERROR_CONFIGS['500']
        return <ErrorDisplay {...errorConfig} />
      }}
    >
      {children}
    </Sentry.ErrorBoundary>
  )
}
