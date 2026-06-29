"""GitHub app pull requests managers."""

from django.db import models


class OpenPullRequestManager(models.Manager):
    """Open pull requests."""

    def get_queryset(self) -> models.QuerySet:
        """Get queryset."""
        return (
            super()
            .get_queryset()
            .select_related(
                "repository",
            )
            .prefetch_related(
                "assignees",
            )
        )
