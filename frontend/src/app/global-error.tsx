'use client'

import { Button } from '@heroui/button'
import { addToast } from '@heroui/toast'
import * as Sentry from '@sentry/nextjs'
import { useRouter } from 'next/navigation'
import React from 'react'

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
  const router = useRouter()
  return (
    <main className="flex flex-1 flex-col items-center justify-center py-9">
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
            onPress={() => router.push('/')}
            className="font-inter bg-owasp-blue mt-8 h-12 w-40 rounded-lg text-base font-medium text-white transition-colors hover:bg-blue-500 dark:bg-slate-800 dark:hover:bg-slate-700"
            aria-label="Return to Home"
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
  let appError: AppError

  if (error instanceof AppError) {
    appError = error
  } else {
    const message = error instanceof Error ? error.message : ERROR_CONFIGS['500'].message
    appError = new AppError(500, message)
  }

  if (appError.statusCode >= 500) {
    Sentry.captureException(error instanceof Error ? error : appError)
  }

  const errorConfig = ERROR_CONFIGS[appError.statusCode === 404 ? '404' : '500']

  addToast({
    title: errorConfig.title,
    description: appError.message || errorConfig.message,
    timeout: 5000,
    variant: 'solid',
    color: 'danger',
    shouldShowTimeoutProgress: true,
  })
}
// Error boundary wrapper component
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

export default function GlobalError({ error }: { error: Error }) {
  Sentry.captureException(error)
  const errorConfig = ERROR_CONFIGS['500']
  return <ErrorDisplay {...errorConfig} />
}
