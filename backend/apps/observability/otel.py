"""OpenTelemetry metrics bootstrap for the backend."""

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

_state = {"configured": False}


def configure_otel_metrics():
    """Configure the OpenTelemetry metrics pipeline and Django instrumentation.

    The service name and OTLP endpoint are read from the standard
    OTEL_SERVICE_NAME and OTEL_EXPORTER_OTLP_ENDPOINT environment variables.
    """
    if _state["configured"]:
        return

    reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    provider = MeterProvider(metric_readers=[reader], resource=Resource.create())
    metrics.set_meter_provider(provider)

    DjangoInstrumentor().instrument(meter_provider=provider)
    _state["configured"] = True
