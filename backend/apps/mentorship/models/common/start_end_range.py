"""Mentorship app start/end range."""

from django.db import models


class StartEndRange(models.Model):
    """Start/end range model."""

    class Meta:
        abstract = True

    ended_at = models.DateTimeField(verbose_name="End date and time")
    started_at = models.DateTimeField(verbose_name="Start date and time")
