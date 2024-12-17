import * as Sentry from '@sentry/react'

import { APPLICATION_SENTRY_URL, APPLICATION_ENV } from './utils/credentials'

Sentry.init({
  dsn: APPLICATION_SENTRY_URL,
  environment: APPLICATION_ENV,
  integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  beforeSend(event) {
    if (event.user) {
      delete event.user.email
    }
    return event
  },
})

export const logException = (error: Error) => Sentry.captureException(error)
export const logMessage = (message: string) => Sentry.captureMessage(message)
