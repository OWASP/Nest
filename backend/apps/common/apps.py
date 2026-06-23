"""Common app config."""

from django.apps import AppConfig
from django.conf import settings

from apps.common.otel import configure_otel_metrics


class CommonConfig(AppConfig):
    """Common app config."""

    name = "apps.common"

    def ready(self):
        """Configure OpenTelemetry metrics when enabled."""
        if settings.OTEL_METRICS_ENABLED:
            configure_otel_metrics()
