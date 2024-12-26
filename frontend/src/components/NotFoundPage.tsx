import React from 'react'

import { ErrorDisplay } from './ErrorDisplay'

export const NotFoundPage: React.FC = () => {
  const notFoundError = {
    code: 'NOT_FOUND',
    statusCode: 404,
    title: 'Page Not Found',
    message: `The page you're looking for doesn't exist.`,
    source: 'routing' as const,
    action: 'home' as const,
  }

  return <ErrorDisplay error={notFoundError} />
}
