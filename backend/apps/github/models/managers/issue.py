"""GitHub app issue managers."""

from django.db import models


class OpenIssueManager(models.Manager):
    """Open issues."""

    def get_queryset(self):
        """Get queryset."""
        return (
            super()
            .get_queryset()
            .select_related(
                "repository",
            )
            .filter(
                repository__project__isnull=False,
                state="open",
            )
        )

    @property
    def without_summary(self):
        """Return issues without summary."""
        return self.get_queryset().filter(summary="")
