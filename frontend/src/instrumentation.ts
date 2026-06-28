import * as Sentry from '@sentry/nextjs'

export async function register() {
  await import('sentry.server.config')

  if (process.env.NEXT_RUNTIME === 'nodejs' && process.env.OTEL_EXPORTER_OTLP_ENDPOINT) {
    const { startMetrics } = await import('./instrumentation-metrics')
    startMetrics()
  }
}

export const onRequestError = Sentry.captureRequestError
