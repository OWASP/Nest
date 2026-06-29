import { metrics } from '@opentelemetry/api'
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-proto'
import { HostMetrics } from '@opentelemetry/host-metrics'
import { defaultResource, resourceFromAttributes } from '@opentelemetry/resources'
import { MeterProvider, PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics'

// Server-side Otel metrics for the Next.js Node runtime. The exporter and
// service name come from the standard OTEL_* environment variables, which are only
// set by the observability compose override (make run-o11y). The protobuf exporter
// is required because VictoriaMetrics rejects JSON-encoded OTLP. Only the meter
// provider is registered here -- tracing is owned by Sentry.
export function startMetrics() {
  const reader = new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter(),
    exportIntervalMillis: Number(process.env.OTEL_METRIC_EXPORT_INTERVAL) || 60_000,
  })

  const provider = new MeterProvider({
    readers: [reader],
    resource: defaultResource().merge(
      resourceFromAttributes({
        'service.name': process.env.OTEL_SERVICE_NAME ?? 'nest-frontend',
      })
    ),
  })

  metrics.setGlobalMeterProvider(provider)

  const hostMetrics = new HostMetrics({ meterProvider: provider })
  hostMetrics.start()
}
