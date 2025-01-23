"""OWASP app contribute model."""

from functools import lru_cache

from django.db import models

from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.core.models.prompt import Prompt
from apps.owasp.models.common import GenericEntityModel, RepositoryBasedEntityModel
from apps.owasp.models.managers.contribute import ActiveContributeManager
from apps.owasp.models.mixins.contribute import ContributeIndexMixin


class Contribute(
    BulkSaveModel,
    ContributeIndexMixin,
    GenericEntityModel,
    RepositoryBasedEntityModel,
    TimestampedModel,
):
    """Contribute model."""

    objects = models.Manager()
    active_contribute = ActiveContributeManager()

    class Meta:
        db_table = "owasp_contribute"
        verbose_name_plural = "Contributions"

    def __str__(self):
        """Contribute human-readable representation."""
        return f"{self.name}"

    def from_github(self, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "name": "title",
            "tags": "tags",
        }
        RepositoryBasedEntityModel.from_github(self, field_mapping, repository)

        if repository:
            self.created_at = repository.created_at
            self.updated_at = repository.updated_at

        # FKs.
        self.owasp_repository = repository

    def save(self, *args, **kwargs):
        """Save contribute instance."""
        if not self.summary and (prompt := Prompt.get_owasp_contribute_summary()):
            self.generate_summary(prompt=prompt)

        super().save(*args, **kwargs)

    @staticmethod
    @lru_cache
    def active_contribute_count():
        """Return active contribute count."""
        return IndexBase.get_total_count("contribute")

    @staticmethod
    def bulk_save(contribute, fields=None):
        """Bulk save contribute."""
        BulkSaveModel.bulk_save(Contribute, contribute, fields=fields)

    @staticmethod
    def update_data(gh_repository, repository, save=True):
        """Update contribute data."""
        key = gh_repository.name.lower()
        try:
            contribute = Contribute.objects.get(key=key)
        except Contribute.DoesNotExist:
            contribute = Contribute(key=key)

        contribute.from_github(repository)
        if save:
            contribute.save()

        return contribute
