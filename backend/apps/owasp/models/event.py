"""OWASP app event model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.common import OwaspEntity


class Event(OwaspEntity, TimestampedModel):
    """Event model."""

    class Meta:
        db_table = "owasp_events"
        verbose_name_plural = "Events"

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    description = models.CharField(
        verbose_name="Description", max_length=500, default="", blank=True
    )
    level = models.CharField(verbose_name="Level", max_length=5, default="", blank=True)

    url = models.URLField(verbose_name="URL", default="", blank=True)

    tags = models.JSONField(verbose_name="Tags", default=list, blank=True)

    owasp_repository = models.ForeignKey(
        "github.Repository", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        """Event human readable representation."""
        return f"{self.name or self.key}"

    def from_github(self, gh_repository, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "level": "level",
            "name": "title",
            "tags": "tags",
        }
        OwaspEntity.from_github(self, field_mapping, gh_repository, repository)

        # FKs.
        self.owasp_repository = repository
