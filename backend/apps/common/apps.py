"""Common app config."""

import logging

from django.apps import AppConfig
from django.conf import settings

from apps.common.otel import configure_otel_metrics

logger = logging.getLogger(__name__)


class CommonConfig(AppConfig):
    """Common app config."""

    name = "apps.common"

    def ready(self):
        """Configure OpenTelemetry metrics when enabled."""
        if settings.OTEL_METRICS_ENABLED:
            try:
                configure_otel_metrics()
            except Exception:
                logger.exception("Failed to configure OpenTelemetry metrics")
