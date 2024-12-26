import * as Sentry from '@sentry/react'

import logger from 'utils/logger'
import type { ErrorConfig } from 'lib/types'

class ErrorService {
  private readonly errorGroups: Map<string, ErrorConfig[]> = new Map([
    [
      'search',
      [
        {
          code: 'ALGOLIA_SEARCH_FAILED',
          title: 'Search Error',
          message: 'Unable to complete search. Please try again.',
          source: 'algolia',
          action: 'retry',
        },
        {
          code: 'ALGOLIA_CONFIG_ERROR',
          title: 'Config Error',
          message: 'Algolia keys not found.',
          source: 'algolia',
          action: 'retry',
        },
        {
          code: 'SEARCH_TIMEOUT',
          title: 'Search Timeout',
          message: 'Search request timed out. Please try again.',
          source: 'network',
          action: 'retry',
        },
      ],
    ],
    [
      'runtime',
      [
        {
          code: 'TYPE_ERROR',
          title: 'Application Error',
          message: 'An error occurred while processing your request.',
          source: 'runtime',
          action: 'retry',
        },
        {
          code: 'REFERENCE_ERROR',
          title: 'Application Error',
          message: 'An error occurred while processing your request.',
          source: 'runtime',
          action: 'retry',
        },
        {
          code: 'SYNTAX_ERROR',
          title: 'Application Error',
          message: 'An error occurred while processing your request.',
          source: 'runtime',
          action: 'home',
        },
      ],
    ],
    [
      'auth',
      [
        {
          code: 'UNAUTHORIZED',
          statusCode: 401,
          title: 'Session Expired',
          message: 'Your session has expired. Please return to home and login again.',
          source: 'http',
          action: 'home',
        },
        {
          code: 'FORBIDDEN',
          statusCode: 403,
          title: 'Access Denied',
          message: "You don't have permission to access this resource.",
          source: 'http',
          action: 'home',
        },
      ],
    ],
    [
      'network',
      [
        {
          code: 'NETWORK_ERROR',
          title: 'Connection Error',
          message: 'Please check your internet connection and try again.',
          source: 'network',
          action: 'retry',
        },
        {
          code: 'SERVER_ERROR',
          statusCode: 500,
          title: 'Server Error',
          message: 'An unexpected server error occurred.',
          source: 'http',
          action: 'retry',
        },
      ],
    ],
  ])

  private readonly httpErrors: Map<number, ErrorConfig> = new Map([
    [
      400,
      {
        code: 'BAD_REQUEST',
        statusCode: 400,
        title: 'Invalid Request',
        message: 'Please check your input and try again.',
        source: 'http',
        action: 'retry',
      },
    ],
    [
      404,
      {
        code: 'NOT_FOUND',
        statusCode: 404,
        title: 'Not Found',
        message: 'The requested resource could not be found.',
        source: 'http',
        action: 'home',
      },
    ],
    [
      429,
      {
        code: 'RATE_LIMIT',
        statusCode: 429,
        title: 'Too Many Requests',
        message: 'Please wait a moment before trying again.',
        source: 'http',
        action: 'home',
      },
    ],
    [
      503,
      {
        code: 'SERVICE_UNAVAILABLE',
        statusCode: 503,
        title: 'Service Unavailable',
        message: 'The service is temporarily unavailable.',
        source: 'http',
        action: 'retry',
      },
    ],
  ])
  private readonly defaultError: ErrorConfig = {
    code: 'UNKNOWN_ERROR',
    title: 'Error',
    message: 'An unexpected error occurred.',
    source: 'runtime',
    action: 'home',
  }

  handleError(error: unknown, context?: string): ErrorConfig {
    try {
      if (this.isHttpError(error)) {
        const status = (error as { status: number }).status
        return this.getHttpError(status)
      }

      if (error instanceof Error) {
        if (error.name === 'NetworkError' && context === 'network') {
          return this.findErrorInGroup('network', 'NETWORK_ERROR') || this.defaultError
        }

        if (context === 'search' && error.name === 'AlgoliaError') {
          return this.findErrorInGroup('search', 'ALGOLIA_SEARCH_FAILED') || this.defaultError
        }
      }

      this.logError(error, this.defaultError)

      return this.defaultError
    } catch {
      return this.defaultError
    }
  }

  private isHttpError(error: unknown): boolean {
    return Boolean(error && typeof error === 'object' && 'status' in error)
  }

  private getHttpError(status: number): ErrorConfig {
    if (status >= 500) {
      return {
        code: 'SERVER_ERROR',
        statusCode: 500,
        title: 'Server Error',
        message: 'An unexpected server error occurred.',
        source: 'http',
        action: 'retry',
      }
    }
    return this.httpErrors.get(status) || this.defaultError
  }

  private findErrorInGroup(groupName: string, code: string): ErrorConfig | undefined {
    const group = this.errorGroups.get(groupName)
    return group?.find((error) => error.code === code)
  }

  private logError(error: unknown, config: ErrorConfig): void {
    const errorContext = {
      error,
      config,
      timestamp: new Date().toISOString(),
    }

    logger.error(`${config.source} Error: ${config.code}`, errorContext)

    Sentry.captureException(error, {
      tags: {
        errorCode: config.code,
        statusCode: config.statusCode,
        source: config.source,
      },
    })
  }
}
export const errorService = new ErrorService()
