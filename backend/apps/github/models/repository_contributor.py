"""Github app label model."""

from django.db import models
from django.template.defaultfilters import pluralize

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.managers.repository_contributor import RepositoryContributorManager

TOP_CONTRIBUTORS_LIMIT = 15


class RepositoryContributor(BulkSaveModel, TimestampedModel):
    """Repository contributor model."""

    objects = RepositoryContributorManager()

    class Meta:
        db_table = "github_repository_contributors"
        unique_together = ("repository", "user")
        verbose_name_plural = "Repository contributors"

    contributions_count = models.PositiveIntegerField(verbose_name="Contributions", default=0)

    # FKs.
    repository = models.ForeignKey(
        "github.Repository",
        verbose_name="Repository",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "github.User",
        verbose_name="User",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Repository contributor human readable representation."""
        return (
            f"{self.user} has made {self.contributions_count} "
            f"contribution{pluralize(self.contributions_count)} to {self.repository}"
        )

    def from_github(self, gh_contributions):
        """Update instance based on GitHub contributor data."""
        field_mapping = {
            "contributions_count": "contributions",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_contributions, gh_field)
            if value is not None:
                setattr(self, model_field, value)

    @staticmethod
    def bulk_save(repository_contributors):
        """Bulk save repository contributors."""
        BulkSaveModel.bulk_save(RepositoryContributor, repository_contributors)

    @staticmethod
    def update_data(gh_contributor, repository, user, save=True):
        """Update repository contributor data."""
        try:
            repository_contributor = RepositoryContributor.objects.get(
                repository=repository,
                user=user,
            )
        except RepositoryContributor.DoesNotExist:
            repository_contributor = RepositoryContributor(
                repository=repository,
                user=user,
            )
        repository_contributor.from_github(gh_contributor)

        if save:
            repository_contributor.save()

        return repository_contributor
