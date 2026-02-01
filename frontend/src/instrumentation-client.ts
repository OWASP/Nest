import * as Sentry from '@sentry/nextjs'
import posthog from 'posthog-js'
import {
  ENVIRONMENT,
  POSTHOG_HOST,
  POSTHOG_KEY,
  RELEASE_VERSION,
  SENTRY_DSN,
} from 'utils/env.client'

Sentry.init({
  debug: false,
  dsn: SENTRY_DSN,
  environment: ENVIRONMENT.toLowerCase(),
  integrations: [Sentry.browserTracingIntegration, Sentry.replayIntegration],
  release: RELEASE_VERSION,
  replaysOnErrorSampleRate: 0.5,
  replaysSessionSampleRate: 0.5,
})

if (POSTHOG_KEY) {
  posthog.init(POSTHOG_KEY, {
    /* eslint-disable @typescript-eslint/naming-convention */
    api_host: POSTHOG_HOST ?? 'https://us.i.posthog.com',
    capture_pageview: 'history_change',
    defaults: '2025-11-30',
    person_profiles: 'identified_only',
    /* eslint-enable @typescript-eslint/naming-convention */
  })
}

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart
