"""Github app milestone manager."""

from django.db import models


class OpenMilestoneManager(models.Manager):
    """Open milestone manager."""

    def get_queryset(self):
        """Get open milestones."""
        return super().get_queryset().filter(state="open")


class ClosedMilestoneManager(models.Manager):
    """Closed milestone manager."""

    def get_queryset(self):
        """Get closed milestones."""
        return super().get_queryset().filter(state="closed")
