import * as Sentry from '@sentry/react'
import { SENTRY_DSN, ENVIRONMENT, RELEASE_VERSION } from 'utils/credentials'

Sentry.init({
  dsn: SENTRY_DSN,
  environment: ENVIRONMENT.toLowerCase(),
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      maskAllText: false,
    }),
  ],
  release: RELEASE_VERSION,
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
  tracesSampleRate: 0.5,
})

export const logException = (error: Error) => Sentry.captureException(error)
export const logCriticalMessage = (message: string) =>
  Sentry.captureMessage(message, { level: 'warning' })
