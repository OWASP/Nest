import * as Sentry from '@sentry/react'
import { SENTRY_DSN, ENVIRONMENT } from 'utils/credentials'

Sentry.init({
  dsn: SENTRY_DSN,
  environment: ENVIRONMENT,
  integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  release: process.env.SENTRY_RELEASE,
})

export const logException = (error: Error) => Sentry.captureException(error)
export const logCriticalMessage = (message: string) =>
  Sentry.captureMessage(message, { level: 'warning' })
