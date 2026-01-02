"""Mentorship app module manager."""

from django.db import models

from apps.mentorship.models.program import Program


class PublishedModuleManager(models.Manager):
    """Published Modules."""

    def get_queryset(self) -> models.QuerySet:
        """Get queryset."""
        return super().get_queryset().filter(program__status=Program.ProgramStatus.PUBLISHED)
