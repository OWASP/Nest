"""Mentorship app matching attributes."""

from django.db import models


class MatchingAttributes(models.Model):
    """Matching attributes model."""

    class Meta:
        """Model options."""

        abstract = True

    domains = models.JSONField(
        verbose_name="Domains",
        default=list,
        blank=True,
        help_text="Domain expertise (e.g., Application Security, Threat Modeling, etc)",
    )

    tags = models.JSONField(
        verbose_name="Tags",
        default=list,
        blank=True,
        help_text="Technologies, languages, frameworks, etc",
    )
