from apps.common import otel


def test_configure_otel_metrics(mocker):
    set_meter_provider = mocker.patch("apps.common.otel.metrics.set_meter_provider")
    meter_provider = mocker.patch("apps.common.otel.MeterProvider")
    mocker.patch("apps.common.otel.PeriodicExportingMetricReader")
    mocker.patch("apps.common.otel.OTLPMetricExporter")
    mocker.patch("apps.common.otel.Resource")
    django_instrumentor = mocker.patch("apps.common.otel.DjangoInstrumentor")

    otel.configure_otel_metrics()

    set_meter_provider.assert_called_once_with(meter_provider.return_value)
    django_instrumentor.return_value.instrument.assert_called_once_with(
        meter_provider=meter_provider.return_value,
    )
