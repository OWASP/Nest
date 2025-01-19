import * as Sentry from '@sentry/react'
import { SENTRY_DSN, ENVIRONMENT, RELEASE_VERSION } from 'utils/credentials'

const getEnvironment = () => {
  try {
    return ENVIRONMENT?.toLowerCase() || 'development'
  } catch {
    return 'development'
  }
}

Sentry.init({
  dsn: SENTRY_DSN || '',
  environment: getEnvironment(),
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      maskAllText: false,
    }),
  ],
  release: RELEASE_VERSION || 'development',
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
  tracesSampleRate: 0.5,
})

export const logException = (error: Error) => Sentry.captureException(error)
export const logCriticalMessage = (message: string) =>
  Sentry.captureMessage(message, { level: 'warning' })
