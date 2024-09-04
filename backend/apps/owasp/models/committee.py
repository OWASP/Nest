"""OWASP app commettee model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.models.common import OwaspEntity


class Committee(BulkSaveModel, OwaspEntity, TimestampedModel):
    """Committee model."""

    class Meta:
        db_table = "owasp_committees"
        verbose_name_plural = "Committees"

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    description = models.CharField(verbose_name="Description", max_length=500, default="")

    tags = models.JSONField(verbose_name="Tags", default=list)

    owasp_repository = models.ForeignKey(
        "github.Repository", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        """Committee human readable representation."""
        return f"{self.name}"

    def from_github(self, gh_repository, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "name": "title",
            "tags": "tags",
        }
        OwaspEntity.from_github(self, field_mapping, gh_repository, repository)

        # FKs.
        self.owasp_repository = repository

    @staticmethod
    def bulk_save(committees):
        """Bulk save committees."""
        BulkSaveModel.bulk_save(Committee, committees)
        committees.clear()

    @staticmethod
    def update_data(gh_repository, repository, save=True):
        """Update committee data."""
        key = gh_repository.name.lower()
        try:
            committee = Committee.objects.get(key=key)
        except Committee.DoesNotExist:
            committee = Committee(key=key)

        committee.from_github(gh_repository, repository)
        if save:
            committee.save()

        return committee
