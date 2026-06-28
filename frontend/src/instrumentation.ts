import * as Sentry from '@sentry/nextjs'

export async function register() {
  await import('sentry.server.config')

  const otlpEndpoint =
    process.env.OTEL_EXPORTER_OTLP_ENDPOINT || process.env.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT

  if (process.env.NEXT_RUNTIME === 'nodejs' && otlpEndpoint) {
    const { startMetrics } = await import('./instrumentation-metrics')
    startMetrics()
  }
}

export const onRequestError = Sentry.captureRequestError
