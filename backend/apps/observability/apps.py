"""Observability app config."""

import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class ObservabilityConfig(AppConfig):
    """Observability app config."""

    name = "apps.observability"

    def ready(self):
        """Configure OpenTelemetry metrics when enabled."""
        if not settings.OTEL_METRICS_ENABLED:
            return

        from apps.observability.otel import configure_otel_metrics

        try:
            configure_otel_metrics()
        except Exception:
            logger.exception("Failed to configure OpenTelemetry metrics")
