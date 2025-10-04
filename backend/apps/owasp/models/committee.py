"""OWASP app committee model."""

from functools import lru_cache

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.core.models.prompt import Prompt
from apps.owasp.models.common import RepositoryBasedEntityModel
from apps.owasp.models.managers.committee import ActiveCommitteeManager
from apps.owasp.models.mixins.committee import CommitteeIndexMixin


class Committee(
    BulkSaveModel,
    CommitteeIndexMixin,
    RepositoryBasedEntityModel,
    TimestampedModel,
):
    """Committee model."""

    objects = models.Manager()
    active_committees = ActiveCommitteeManager()

    class Meta:
        db_table = "owasp_committees"
        verbose_name_plural = "Committees"

    # GRs.
    members = GenericRelation("owasp.EntityMember")

    def __str__(self) -> str:
        """Committee human readable representation."""
        return f"{self.name}"

    def from_github(self, repository, gh) -> None:
        """Update instance based on GitHub repository data."""
        self.owasp_repository = repository

        RepositoryBasedEntityModel.from_github(
            self,
            {
                "description": "pitch",
                "name": "title",
                "tags": "tags",
            },
            gh,
        )

        self.created_at = repository.created_at
        self.updated_at = repository.updated_at

    def save(self, *args, **kwargs) -> None:
        """Save committee."""
        if not self.summary and (prompt := Prompt.get_owasp_committee_summary()):
            self.generate_summary(prompt=prompt)

        super().save(*args, **kwargs)

    @property
    def nest_key(self):
        """Get Nest key."""
        return self.key.replace("www-committee-", "")

    @staticmethod
    @lru_cache
    def active_committees_count():
        """Return active committees count."""
        return IndexBase.get_total_count("committees")

    @staticmethod
    def bulk_save(committees, fields=None) -> None:  # type: ignore[override]
        """Bulk save committees."""
        BulkSaveModel.bulk_save(Committee, committees, fields=fields)

    @staticmethod
    def update_data(gh_repository, repository, gh, *, save: bool = True) -> "Committee":
        """Update committee data."""
        key = gh_repository.name.lower()
        try:
            committee = Committee.objects.get(key=key)
        except Committee.DoesNotExist:
            committee = Committee(key=key)

        committee.from_github(repository, gh)
        if save:
            committee.save()

        return committee
