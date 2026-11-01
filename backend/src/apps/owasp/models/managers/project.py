"""OWASP app project managers."""

from django.db import models


class ActiveProjectManager(models.Manager):
    """Active projects."""

    def get_queryset(self) -> models.QuerySet:
        """Get queryset."""
        return super().get_queryset().filter(is_active=True)

    @property
    def without_summary(self) -> models.QuerySet:
        """Return projects without summary."""
        return self.get_queryset().filter(summary="")
