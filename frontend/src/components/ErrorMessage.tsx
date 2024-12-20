import React from 'react'
import { useNavigate } from 'react-router-dom'
interface ErrorMessageProps {
  message: string
  statusCode?: number
  onRetry?: () => void
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, statusCode, onRetry }) => {
  const navigate = useNavigate()

  const handleBackToHome = () => {
    navigate('/')
  }

  return (
    <div className="relative rounded border border-red-400 bg-red-100 px-4 py-3 text-red-700">
      <span className="mr-4 inline-block align-middle">
        <svg
          className="h-5 w-5"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h4a1 1 0 001-1v-3a1 1 0 00-1-1H9z"
            clipRule="evenodd"
          />
        </svg>
      </span>
      <span className="inline-block align-middle">
        {statusCode ? `Error ${statusCode}: ${message}` : message}
      </span>
      <div className="mt-4 flex space-x-4">
        {onRetry ? (
          <button onClick={onRetry} className="rounded bg-blue-500 px-4 py-2 text-white">
            Retry
          </button>
        ) : (
          <button onClick={handleBackToHome} className="rounded bg-blue-500 px-4 py-2 text-white">
            Back to Home
          </button>
        )}
      </div>
    </div>
  )
}

export default ErrorMessage
