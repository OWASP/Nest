import { logException, logMessage } from '../sentry.config'
import { APPLICATION_ENV } from '../utils/credentials'

/**
 * Logger utility for handling logs and errors.
 * In development, logs are printed to the console.
 * In production, logs and errors are sent to Sentry.
 */
export const logger = {
  log: (...args: unknown[]) => {
    const message = args
      .map((arg) => (typeof arg === 'string' ? arg : JSON.stringify(arg)))
      .join(' ')

    if (APPLICATION_ENV === 'development') {
      console.log(...args)
    } else {
      logMessage(message)
    }
  },

  error: (...args: unknown[]) => {
    if (APPLICATION_ENV === 'development') {
      console.error(...args)
    } else {
      args.forEach((arg) => {
        if (arg instanceof Error) {
          logException(arg)
        } else {
          const message = typeof arg === 'string' ? arg : JSON.stringify(arg)
          logMessage(message)
        }
      })
    }
  },
}

export default logger
