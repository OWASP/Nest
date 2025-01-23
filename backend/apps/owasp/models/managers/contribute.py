"""OWASP app contribute managers."""

from django.db import models


class ActiveContributeManager(models.Manager):
    """Active contribute."""

    def get_queryset(self):
        """Get queryset."""
        return super().get_queryset().filter(is_active=True)

    @property
    def without_summary(self):
        """Return contribute without summary."""
        return self.get_queryset().filter(summary="")
