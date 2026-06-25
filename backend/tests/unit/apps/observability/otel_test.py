from apps.observability import otel


def test_configure_otel_metrics(mocker):
    otel._state["configured"] = False
    set_meter_provider = mocker.patch("apps.observability.otel.metrics.set_meter_provider")
    meter_provider = mocker.patch("apps.observability.otel.MeterProvider")
    mocker.patch("apps.observability.otel.PeriodicExportingMetricReader")
    mocker.patch("apps.observability.otel.OTLPMetricExporter")
    mocker.patch("apps.observability.otel.Resource")
    django_instrumentor = mocker.patch("apps.observability.otel.DjangoInstrumentor")

    otel.configure_otel_metrics()

    set_meter_provider.assert_called_once_with(meter_provider.return_value)
    django_instrumentor.return_value.instrument.assert_called_once_with(
        meter_provider=meter_provider.return_value,
    )


def test_configure_otel_metrics_is_idempotent(mocker):
    otel._state["configured"] = False
    mocker.patch("apps.observability.otel.metrics.set_meter_provider")
    mocker.patch("apps.observability.otel.MeterProvider")
    mocker.patch("apps.observability.otel.PeriodicExportingMetricReader")
    mocker.patch("apps.observability.otel.OTLPMetricExporter")
    mocker.patch("apps.observability.otel.Resource")
    django_instrumentor = mocker.patch("apps.observability.otel.DjangoInstrumentor")

    otel.configure_otel_metrics()
    otel.configure_otel_metrics()

    django_instrumentor.return_value.instrument.assert_called_once()
