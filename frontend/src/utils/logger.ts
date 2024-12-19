import { logException, logCriticalMessage } from '../sentry.config'
import { APPLICATION_ENV } from '../utils/credentials'

/**
 * Logger utility for handling logs and errors.
 * In development, logs are printed to the console.
 * In production:
 * - Logs are routed to console...i.e only errors are sent to Sentry
 * - Errors and critical issues are sent to Sentry.
 */

export const logger = {
  log: (...args: unknown[]) => {
    const message = args
      .map((arg) => (typeof arg === 'string' ? arg : JSON.stringify(arg)))
      .join(' ')
    console.log(message)
  },

  error: (...args: unknown[]) => {
    if (APPLICATION_ENV === 'development' || APPLICATION_ENV === 'local') {
      console.error(...args)
    } else {
      args.forEach((arg) => {
        if (arg instanceof Error) {
          logException(arg)
        } else {
          const message = typeof arg === 'string' ? arg : JSON.stringify(arg)
          logCriticalMessage(message)
        }
      })
    }
  },
}

export default logger
