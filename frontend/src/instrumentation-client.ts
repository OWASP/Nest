import * as Sentry from '@sentry/nextjs'
import posthog from 'posthog-js'
import {
  ENVIRONMENT,
  RELEASE_VERSION,
  SENTRY_DSN,
  POSTHOG_KEY,
  POSTHOG_HOST,
} from 'utils/env.client'

const env = ENVIRONMENT?.toLowerCase() || 'local'
const isTrackingEnabled = env === 'production' || env === 'staging'

Sentry.init({
  debug: false,
  dsn: SENTRY_DSN,
  environment: ENVIRONMENT.toLowerCase(),
  integrations: [Sentry.browserTracingIntegration, Sentry.replayIntegration],
  release: RELEASE_VERSION,
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
})

if (isTrackingEnabled && POSTHOG_KEY) {
  posthog.init(POSTHOG_KEY, {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    api_host: POSTHOG_HOST,
    defaults: '2025-11-30',
    // eslint-disable-next-line @typescript-eslint/naming-convention
    person_profiles: 'identified_only',
    // eslint-disable-next-line @typescript-eslint/naming-convention
    capture_pageview: true,
  })
}

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart
