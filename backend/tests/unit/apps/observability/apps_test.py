from apps.observability.apps import ObservabilityConfig


class TestObservabilityConfig:
    def test_ready_configures_otel_when_enabled(self, mocker, settings):
        settings.OTEL_METRICS_ENABLED = True
        configure = mocker.patch("apps.observability.otel.configure_otel_metrics")

        ObservabilityConfig.ready(mocker.Mock())

        configure.assert_called_once()

    def test_ready_skips_otel_when_disabled(self, mocker, settings):
        settings.OTEL_METRICS_ENABLED = False
        configure = mocker.patch("apps.observability.otel.configure_otel_metrics")

        ObservabilityConfig.ready(mocker.Mock())

        configure.assert_not_called()

    def test_ready_swallows_otel_errors(self, mocker, settings):
        settings.OTEL_METRICS_ENABLED = True
        mocker.patch(
            "apps.observability.otel.configure_otel_metrics",
            side_effect=RuntimeError("boom"),
        )

        ObservabilityConfig.ready(mocker.Mock())
