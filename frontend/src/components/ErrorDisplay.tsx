import React from 'react'
import { useNavigate } from 'react-router-dom'

import { ErrorConfig } from 'lib/types'

interface ErrorDisplayProps {
  error: ErrorConfig
  onRetry?: () => void
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
  const navigate = useNavigate()

  return (
    <main className="flex min-h-screen flex-col items-center bg-white pt-8 dark:bg-slate-900">
      <div className="flex flex-1 flex-col items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <h1 className="font-poppins text-8xl font-semibold leading-normal text-black dark:text-white">
            {error.statusCode}
          </h1>
        </div>

        <div className="w-full max-w-md text-center">
          <h2 className="font-inter text-2xl font-semibold leading-normal text-black dark:text-white">
            {error.title}
          </h2>
        </div>

        <div className="mt-2 w-full max-w-2xl text-center">
          <p className="font-inter text-lg font-normal leading-relaxed text-black dark:text-white">
            {error.message}
          </p>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-4">
          {error.action === 'retry' && onRetry && (
            <button
              onClick={onRetry}
              className="font-inter h-12 w-40 rounded-lg bg-owasp-blue text-base font-medium text-white transition-colors hover:bg-blue-400"
            >
              Try Again
            </button>
          )}
          <button
            onClick={() => navigate('/')}
            className="font-inter h-12 w-40 rounded-lg bg-owasp-blue text-base font-medium text-white transition-colors hover:bg-blue-400"
          >
            Return To Home
          </button>
        </div>
      </div>
    </main>
  )
}
