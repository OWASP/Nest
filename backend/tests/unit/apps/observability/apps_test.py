from apps.observability.apps import ObservabilityConfig


def test_ready_configures_otel_when_enabled(mocker, settings):
    settings.OTEL_METRICS_ENABLED = True
    configure = mocker.patch("apps.observability.apps.configure_otel_metrics")

    ObservabilityConfig.ready(mocker.Mock())

    configure.assert_called_once()


def test_ready_skips_otel_when_disabled(mocker, settings):
    settings.OTEL_METRICS_ENABLED = False
    configure = mocker.patch("apps.observability.apps.configure_otel_metrics")

    ObservabilityConfig.ready(mocker.Mock())

    configure.assert_not_called()


def test_ready_swallows_otel_errors(mocker, settings):
    settings.OTEL_METRICS_ENABLED = True
    mocker.patch(
        "apps.observability.apps.configure_otel_metrics",
        side_effect=RuntimeError("boom"),
    )

    ObservabilityConfig.ready(mocker.Mock())
