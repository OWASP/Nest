from apps.common.apps import CommonConfig


def test_ready_configures_otel_when_enabled(mocker, settings):
    settings.OTEL_METRICS_ENABLED = True
    configure = mocker.patch("apps.common.apps.configure_otel_metrics")

    CommonConfig.ready(mocker.Mock())

    configure.assert_called_once()


def test_ready_skips_otel_when_disabled(mocker, settings):
    settings.OTEL_METRICS_ENABLED = False
    configure = mocker.patch("apps.common.apps.configure_otel_metrics")

    CommonConfig.ready(mocker.Mock())

    configure.assert_not_called()
