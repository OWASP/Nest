"""Github app label model."""

from __future__ import annotations

from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import pluralize

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.managers.repository_contributor import RepositoryContributorManager

# Matches a full name starting with at least two Unicode letters (no digits or underscores),
# followed by one or more space-separated parts that are either a single letter with a period or
# another sequence of at least two letters.
CONTRIBUTOR_FULL_NAME_REGEX = r"[^\W\d_]{2,}(\s+([^\W\d_]\.|[^\W\d_]{2,}))+"


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
    ) -> RepositoryContributor:
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
        *,
        chapter=None,
        committee=None,
        excluded_usernames: list[str] | None = None,
        has_full_name=False,
        limit=15,
        organization=None,
        project=None,
        repository=None,
    ):
        """Get top contributors across repositories, organization, or project.

        Args:
            chapter (str, optional): Chapter key to filter by.
            committee (str, optional): Committee key to filter by.
            excluded_usernames (list[str], optional): Usernames to exclude from the results.
            has_full_name (bool, optional): Filter contributors with likely full names.
            limit (int, optional): Maximum number of contributors to return.
            organization (str, optional): Organization login to filter by.
            project (str, optional): Project key to filter by.
            repository (str, optional): Repository key to filter by.

        Returns:
            list: List of dictionaries containing contributor information.

        """
        queryset = (
            cls.objects.by_humans()
            .to_community_repositories()
            .select_related("repository__project", "user")
        )

        if excluded_usernames:
            queryset = queryset.exclude(user__login__in=excluded_usernames)

        if has_full_name:
            queryset = queryset.filter(user__name__regex=CONTRIBUTOR_FULL_NAME_REGEX)

        if project:
            queryset = queryset.filter(repository__project__key__iexact=f"www-project-{project}")
        elif chapter:
            queryset = queryset.filter(repository__key__iexact=f"www-chapter-{chapter}")
        elif committee:
            queryset = queryset.filter(repository__key__iexact=f"www-committee-{committee}")

        if organization:
            queryset = queryset.select_related(
                "repository__organization",
            ).filter(
                repository__organization__login=organization,
            )

        if repository:
            queryset = queryset.filter(repository__name__iexact=repository)

        # Project contributors only for main/project/organization pages.
        if not (chapter or committee or repository):
            queryset = queryset.filter(repository__project__isnull=False)

        # Aggregate total contributions for users.
        top_contributors = (
            (
                queryset.values(
                    "user__avatar_url",
                    "user__login",
                    "user__name",
                )
                .annotate(
                    total_contributions=Sum("contributions_count"),
                )
                .order_by("-total_contributions")[:limit]
            )
            if limit > 0
            else []
        )

        return [
            {
                "avatar_url": tc["user__avatar_url"],
                "contributions_count": tc["total_contributions"],
                "id": tc["user__login"],
                "login": tc["user__login"],
                "name": tc["user__name"],
            }
            for tc in top_contributors
        ]
