import * as Sentry from '@sentry/react'
import React from 'react'
import { toast } from 'react-hot-toast'
import { NavigateFunction, useNavigate } from 'react-router-dom'

interface ErrorDisplayConfig {
  statusCode: number
  title: string
  message: string
}

export const ERROR_CONFIGS: Record<string, ErrorDisplayConfig> = {
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
  default: {
    statusCode: 400,
    title: 'Error',
    message: 'Something went wrong',
  },
}

export const ErrorDisplay: React.FC<ErrorDisplayConfig> = ({ statusCode, title, message }) => {
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

export const handleError = (
  error: unknown,
  navigate?: NavigateFunction
): React.ReactElement | void => {
  // Log all errors to Sentry
  Sentry.captureException(error)

  if (error instanceof Error) {
    switch (error.name) {
      case 'NotFoundError':
        return <ErrorDisplay {...ERROR_CONFIGS['404']} />

      case 'ServerError':
        return <ErrorDisplay {...ERROR_CONFIGS['500']} />

      default:
        toast.error(ERROR_CONFIGS['default'].message)
        navigate?.('/')
        return
    }
  }

  toast.error(ERROR_CONFIGS['default'].message)
  navigate?.('/')
}
