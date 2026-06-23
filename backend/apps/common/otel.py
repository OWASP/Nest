"""OpenTelemetry metrics bootstrap for the backend."""

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


def configure_otel_metrics():
    """Configure the OpenTelemetry metrics pipeline and Django instrumentation."""
    reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    provider = MeterProvider(metric_readers=[reader], resource=Resource.create())
    metrics.set_meter_provider(provider)

    DjangoInstrumentor().instrument(meter_provider=provider)
