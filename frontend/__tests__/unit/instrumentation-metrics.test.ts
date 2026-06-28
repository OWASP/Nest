import { metrics } from '@opentelemetry/api'
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-proto'
import { HostMetrics } from '@opentelemetry/host-metrics'
import { resourceFromAttributes } from '@opentelemetry/resources'
import { MeterProvider, PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics'
import { startMetrics } from 'instrumentation-metrics'

jest.mock('@opentelemetry/api', () => ({
  metrics: { setGlobalMeterProvider: jest.fn() },
}))
jest.mock('@opentelemetry/exporter-metrics-otlp-proto', () => ({
  // eslint-disable-next-line @typescript-eslint/naming-convention -- mocked module export name
  OTLPMetricExporter: jest.fn(),
}))
jest.mock('@opentelemetry/host-metrics', () => ({
  // eslint-disable-next-line @typescript-eslint/naming-convention -- mocked module export name
  HostMetrics: jest.fn(() => ({ start: jest.fn() })),
}))
jest.mock('@opentelemetry/resources', () => ({
  resourceFromAttributes: jest.fn((attributes) => attributes),
}))
jest.mock('@opentelemetry/sdk-metrics', () => ({
  // eslint-disable-next-line @typescript-eslint/naming-convention -- mocked module export name
  MeterProvider: jest.fn(),
  // eslint-disable-next-line @typescript-eslint/naming-convention -- mocked module export name
  PeriodicExportingMetricReader: jest.fn(),
}))

describe('startMetrics', () => {
  const originalEnv = process.env

  beforeEach(() => {
    jest.clearAllMocks()
    process.env = { ...originalEnv }
  })

  afterAll(() => {
    process.env = originalEnv
  })

  test('wires the protobuf exporter, reader, provider, and host metrics from env', () => {
    process.env.OTEL_SERVICE_NAME = 'custom-service'
    process.env.OTEL_METRIC_EXPORT_INTERVAL = '15000'

    startMetrics()

    expect(OTLPMetricExporter).toHaveBeenCalledTimes(1)
    expect(PeriodicExportingMetricReader).toHaveBeenCalledWith({
      exporter: expect.any(OTLPMetricExporter),
      exportIntervalMillis: 15000,
    })
    expect(resourceFromAttributes).toHaveBeenCalledWith({ 'service.name': 'custom-service' })
    expect(MeterProvider).toHaveBeenCalledWith({
      readers: [expect.any(PeriodicExportingMetricReader)],
      resource: { 'service.name': 'custom-service' },
    })
    expect(metrics.setGlobalMeterProvider).toHaveBeenCalledWith(expect.any(MeterProvider))
    expect(HostMetrics).toHaveBeenCalledWith({ meterProvider: expect.any(MeterProvider) })
  })

  test('falls back to defaults when env vars are unset', () => {
    delete process.env.OTEL_SERVICE_NAME
    delete process.env.OTEL_METRIC_EXPORT_INTERVAL

    startMetrics()

    expect(PeriodicExportingMetricReader).toHaveBeenCalledWith(
      expect.objectContaining({ exportIntervalMillis: 60000 })
    )
    expect(resourceFromAttributes).toHaveBeenCalledWith({ 'service.name': 'nest-frontend' })
  })

  test('starts host metrics collection', () => {
    startMetrics()

    const instance = (HostMetrics as jest.Mock).mock.results[0].value
    expect(instance.start).toHaveBeenCalledTimes(1)
  })
})
