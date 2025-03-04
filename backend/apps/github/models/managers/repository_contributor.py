"""GitHub app issue managers."""

from django.db import models

from apps.github.constants import OWASP_GITHUB_IO
from apps.github.models.user import User


class RepositoryContributorQuerySet(models.QuerySet):
    """Repository contributor queryset."""

    def by_humans(self):
        """Return human repository contributors only."""
        return self.filter(user__is_bot=False).exclude(
            user__login__in=User.get_non_indexable_logins()
        )

    def to_community_repositories(self):
        """Return community repositories contributors only."""
        return self.exclude(repository__name__in=(OWASP_GITHUB_IO,))


class RepositoryContributorManager(models.Manager):
    """Repository contributor manager."""

    def get_queryset(self):
        """Get queryset."""
        return RepositoryContributorQuerySet(
            self.model,
            using=self._db,
        ).select_related(
            "repository",
            "user",
        )

    def by_humans(self):
        """Return human contributors only."""
        return self.get_queryset().by_humans()

    def to_community_repositories(self):
        """Return community repository contributors only."""
        return self.get_queryset().to_community_repositories()
