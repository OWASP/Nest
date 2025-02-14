"""OWASP app committee managers."""

#!/usr/bin/env python3
from django.db import models


class ActiveCommitteeManager(models.Manager):
    """Active committees."""

    def get_queryset(self):
        """Get queryset."""
        return super().get_queryset().filter(is_active=True)

    @property
    def without_summary(self):
        """Return committees without summary."""
        return self.get_queryset().filter(summary="")
