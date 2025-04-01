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
        indexes = [
            models.Index(
                fields=["user", "-contributions_count"], name="user_contributions_count_idx"
            ),
        ]
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
        """Return a human-readable representation of the repository contributor.

        Returns
            str: A string describing the user's contributions to the repository.

        """
        return (
            f"{self.user} has made {self.contributions_count} "
            f"contribution{pluralize(self.contributions_count)} to {self.repository}"
        )

    def from_github(self, gh_contributions):
        """Update the instance based on GitHub contributor data.

        Args:
            gh_contributions (github.NamedUser.Contributor): The GitHub contributor object.

        """
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
        """Update repository contributor data.

        Args:
            gh_contributor (github.NamedUser.Contributor): The GitHub contributor object.
            repository (Repository): The repository instance.
            user (User): The user instance.
            save (bool, optional): Whether to save the instance.

        Returns:
            RepositoryContributor: The updated or created repository contributor instance.

        """
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
