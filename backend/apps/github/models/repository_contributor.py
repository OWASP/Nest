"""Github app label model."""

from django.db import models
from django.db.models import F, Sum, Window
from django.db.models.functions import Rank
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

    def __str__(self) -> str:
        """Return a human-readable representation of the repository contributor.

        Returns:
            str: A string describing the user's contributions to the repository.

        """
        return (
            f"{self.user} has made {self.contributions_count} "
            f"contribution{pluralize(self.contributions_count)} to {self.repository}"
        )

    def from_github(self, gh_contributions) -> None:
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
    def bulk_save(repository_contributors) -> None:  # type: ignore[override]
        """Bulk save repository contributors."""
        BulkSaveModel.bulk_save(RepositoryContributor, repository_contributors)

    @staticmethod
    def update_data(
        gh_contributor,
        repository,
        user,
        *,
        save: bool = True,
    ) -> "RepositoryContributor":
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

    @classmethod
    def get_top_contributors(
        cls,
        limit=TOP_CONTRIBUTORS_LIMIT,
        chapter=None,
        committee=None,
        organization=None,
        project=None,
        repositories=None,
        repository=None,
    ):
        """Get top contributors across repositories, organization, or project.

        Args:
            limit (int, optional): Maximum number of contributors to return.
            chapter (str, optional): Chapter key to filter by.
            committee (str, optional): Committee key to filter by.
            organization (str, optional): Organization login to filter by.
            project (str, optional): Project key to filter by.
            repositories (QuerySet or list, optional): Repositories to filter by.
            repository (str, optional): Repository key to filter by.

        Returns:
            list: List of dictionaries containing contributor information.

        """
        queryset = (
            cls.objects.by_humans()
            .to_community_repositories()
            .select_related("repository__project", "user")
        )

        if repositories:
            queryset = queryset.filter(repository__in=repositories)

        if organization:
            queryset = queryset.select_related(
                "repository__organization",
            ).filter(
                repository__organization__login=organization,
            )

        if project:
            queryset = queryset.filter(repository__project__key__iexact=f"www-project-{project}")

        if chapter:
            queryset = queryset.filter(repository__chapter__key__iexact=f"www-chapter-{chapter}")

        if committee:
            queryset = queryset.filter(
                repository__committee__key__iexact=f"www-committee-{committee}"
            )

        if repository:
            queryset = queryset.filter(repository__name__iexact=repository)

        if not repositories:
            # Only apply project filter when not filtering by repositories
            queryset = queryset.filter(repository__project__isnull=False)

            # Rank by contributions when looking across repositories
            queryset = queryset.annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=F("contributions_count").desc(),
                    partition_by=F("user__login"),
                )
            )

            # Get top contributor per user
            queryset = queryset.filter(rank=1)

        # Aggregate total contributions for users
        result = queryset.values(
            "user__avatar_url",
            "user__login",
            "user__name",
        ).annotate(total_contributions=Sum("contributions_count"))

        # Add project information if we're not querying by project or organization
        if not project and not organization and not repositories:
            result = result.annotate(
                project_name=F("repository__project__name"),
                project_key=F("repository__project__key"),
            )

        # Order and limit
        result = result.order_by("-total_contributions")[:limit]

        # Format the result
        return [
            {
                "avatar_url": item["user__avatar_url"],
                "contributions_count": item["total_contributions"],
                "login": item["user__login"],
                "name": item["user__name"],
                "project_key": item.get("project_key", "").replace("www-project-", "")
                if item.get("project_key")
                else None,
                "project_name": item.get("project_name"),
            }
            for item in result
        ]
