"""OWASP app commettee model."""

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.models.common import RepositoryBasedEntityModel


class Committee(BulkSaveModel, RepositoryBasedEntityModel, TimestampedModel):
    """Committee model."""

    class Meta:
        db_table = "owasp_committees"
        verbose_name_plural = "Committees"

    def __str__(self):
        """Committee human readable representation."""
        return f"{self.name}"

    def from_github(self, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "name": "title",
            "tags": "tags",
        }
        RepositoryBasedEntityModel.from_github(self, field_mapping, repository)

        # FKs.
        self.owasp_repository = repository

    @staticmethod
    def bulk_save(committees):
        """Bulk save committees."""
        BulkSaveModel.bulk_save(Committee, committees)

    @staticmethod
    def update_data(gh_repository, repository, save=True):
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
