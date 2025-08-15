import * as Sentry from '@sentry/nextjs'
import { SENTRY_DSN, ENVIRONMENT, RELEASE_VERSION } from 'utils/credentials'
const DSN = SENTRY_DSN || process.env.SENTRY_DSN || ''
const isSentryEnabled = !!DSN

Sentry.init({
  dsn: DSN,
  enabled: isSentryEnabled,
  environment: ENVIRONMENT.toLowerCase(),
  release: RELEASE_VERSION,
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
  tracesSampleRate: 0.5,
})