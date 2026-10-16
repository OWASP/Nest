"""OWASP app committee model."""

from __future__ import annotations

from functools import lru_cache

from django.db import models

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
        """Model options."""

        db_table = "owasp_committees"
        verbose_name_plural = "Committees"

    def __str__(self) -> str:
        """Committee human readable representation."""
        return f"{self.name}"

    def from_github(self, repository) -> None:
        """Update instance based on GitHub repository data."""
        self.owasp_repository = repository

        RepositoryBasedEntityModel.from_github(
            self,
            {
                "description": "pitch",
                "name": "title",
                "tags": "tags",
            },
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
        return self.key

    @classmethod
    def get_by_key(cls, key: str, *, active_only: bool = True) -> Committee | None:
        """Return the committee stored under this key.

        A slug also matches a stored ``www-committee-`` key when that row has not been renamed yet.

        Args:
            key (str): Committee key.
            active_only (bool): Limit the lookup to active committees. Pass False to include
                inactive committees.

        Returns:
            Committee | None: The matching committee, if one exists.

        """
        queryset = cls.active_committees if active_only else cls.objects
        normalized = key.strip()
        committee = queryset.filter(key__iexact=normalized).first()
        if committee is not None or normalized.lower().startswith("www-committee-"):
            return committee
        return queryset.filter(key__iexact=f"www-committee-{normalized}").first()

    @staticmethod
    @lru_cache
    def active_committees_count():
        """Return active committees count."""
        return Committee.objects.filter(
            has_active_repositories=True,
        ).count()

    @staticmethod
    def bulk_save(committees, fields=None) -> None:  # type: ignore[override]
        """Bulk save committees."""
        BulkSaveModel.bulk_save(Committee, committees, fields=fields)

    @staticmethod
    def update_data(gh_repository, repository, *, save: bool = True) -> Committee:
        """Update committee data."""
        key = gh_repository.name.lower()
        try:
            committee = Committee.objects.get(key=key)
        except Committee.DoesNotExist:
            committee = Committee(key=key)

        committee.from_github(repository)
        if save:
            committee.save()

        return committee
