import * as Sentry from '@sentry/nextjs'
import { SENTRY_DSN, ENVIRONMENT, RELEASE_VERSION } from 'utils/credentials'

Sentry.init({
  dsn: SENTRY_DSN || '',
  enabled: !!SENTRY_DSN,
  environment: ENVIRONMENT.toLowerCase(),
  release: RELEASE_VERSION,
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
  tracesSampleRate: 0.5,
})
