"""OWASP app project managers."""

#!/usr/bin/env python3
from django.db import models


class ActiveProjectManager(models.Manager):
    """Active projects."""

    def get_queryset(self):
        """Get queryset."""
        return super().get_queryset().filter(is_active=True)

    @property
    def without_summary(self):
        """Return projects without summary."""
        return self.get_queryset().filter(summary="")
