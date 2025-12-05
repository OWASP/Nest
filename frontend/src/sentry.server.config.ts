import * as Sentry from '@sentry/nextjs'

const ENVIRONMENT = process.env.ENVIRONMENT || "development";
const RELEASE_VERSION = process.env.RELEASE_VERSION || "0.0.1";
const SENTRY_DSN = process.env.SENTRY_DSN || "";

Sentry.init({
  dsn: SENTRY_DSN,
  enabled: !!SENTRY_DSN,
  environment: ENVIRONMENT.toLowerCase(),
  release: RELEASE_VERSION,
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
  tracesSampleRate: 0.5,
})
