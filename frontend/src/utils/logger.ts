import { APPLICATION_ENV } from './credentials'

/**
 * This is the central logging configuration for the Nest.
 * In development, logs are output to the console.
 * In production, logs will be sent to Sentry (or a centralized logging service) for error tracking and monitoring.
 * Sentry integration should be implemented here to ensure centralized and scalable error handling.
 */

const logger = {
  log: (...args: unknown[]) => {
    if (APPLICATION_ENV === 'development') {
      // Development logging: Output general information to the console.
      console.log(...args)
    } else {
      // Production logging: In the future, general information logs will be sent to a centralized logging service i.e Sentry
    }
  },
  warn: (...args: unknown[]) => {
    if (APPLICATION_ENV === 'development') {
      // Development logging: Output warnings to the console.
      console.warn(...args)
    } else {
      // Production logging: In the future, warnings will be sent to a centralized logging service.
      // Include relevant context and metadata.
    }
  },
  error: (...args: unknown[]) => {
    if (APPLICATION_ENV === 'development') {
      // Development logging: Output errors to the console.
      console.error(...args)
    } else {
      // Production logging: In the future, errors will be sent to Sentry for error tracking and alerting.
      // Consider setting up error monitoring dashboards and alerts in Sentry.
    }
  },
}

export default logger
