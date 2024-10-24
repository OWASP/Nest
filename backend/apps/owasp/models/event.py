"""OWASP app event model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.models.common import RepositoryBasedEntityModel


class Event(BulkSaveModel, RepositoryBasedEntityModel, TimestampedModel):
    """Event model."""

    class Meta:
        db_table = "owasp_events"
        verbose_name_plural = "Events"

    level = models.CharField(verbose_name="Level", max_length=5, default="", blank=True)
    url = models.URLField(verbose_name="URL", default="", blank=True)

    owasp_repository = models.ForeignKey(
        "github.Repository", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        """Event human readable representation."""
        return f"{self.name or self.key}"

    def from_github(self, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "level": "level",
            "name": "title",
            "tags": "tags",
        }
        RepositoryBasedEntityModel.from_github(self, field_mapping, repository)

        # FKs.
        self.owasp_repository = repository

    @staticmethod
    def bulk_save(events, fields=None):
        """Bulk save events."""
        BulkSaveModel.bulk_save(Event, events, fields=fields)

    @staticmethod
    def update_data(gh_repository, repository, save=True):
        """Update event data."""
        key = gh_repository.name.lower()
        try:
            event = Event.objects.get(key=key)
        except Event.DoesNotExist:
            event = Event(key=key)

        event.from_github(repository)
        if save:
            event.save()

        return event
