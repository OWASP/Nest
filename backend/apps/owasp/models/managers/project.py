"""OWASP app project managers."""

from django.db import models


class ActiveProjectManager(models.Manager):
    """Active projects."""

    def get_queryset(self):
        """Get queryset."""
        return super().get_queryset().filter(is_active=True)
