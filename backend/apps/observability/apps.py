"""Observability app config."""

import logging

from django.apps import AppConfig
from django.conf import settings

from apps.observability.otel import configure_otel_metrics

logger = logging.getLogger(__name__)


class ObservabilityConfig(AppConfig):
    """Observability app config."""

    name = "apps.observability"

    def ready(self):
        """Configure OpenTelemetry metrics when enabled."""
        if settings.OTEL_METRICS_ENABLED:
            try:
                configure_otel_metrics()
            except Exception:
                logger.exception("Failed to configure OpenTelemetry metrics")
