import * as Sentry from '@sentry/nextjs'
import { ENVIRONMENT, RELEASE_VERSION, SENTRY_DSN } from 'utils/credentials'

Sentry.init({
  debug: false,
  dsn: SENTRY_DSN,
  environment: ENVIRONMENT.toLowerCase(),
  integrations: [Sentry.browserTracingIntegration, Sentry.replayIntegration],
  release: RELEASE_VERSION,
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
})

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart
