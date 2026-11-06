"""Completed contribution synchronization coverage for a repository."""

from django.db import models

from apps.common.models import TimestampedModel


class RepositoryContributionSyncState(TimestampedModel):
    """Track verified coverage independently of the contribution records present."""

    class ContributionType(models.TextChoices):
        """Contribution categories synchronized independently."""

        COMMITS = "commits", "Commits"
        ISSUES = "issues", "Issues"
        PULL_REQUESTS = "pull_requests", "Pull requests"

    repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.CASCADE,
        related_name="contribution_sync_states",
    )
    contribution_type = models.CharField(max_length=13, choices=ContributionType.choices)
    covered_from = models.DateTimeField(
        null=True, blank=True, help_text="Start of continuous, successfully collected history."
    )
    covered_until = models.DateTimeField(
        null=True, blank=True, help_text="Captured run-start time of the last completed sync."
    )
    default_branch = models.CharField(max_length=100, blank=True, default="")
    last_head_sha = models.CharField(max_length=64, blank=True, default="")
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(
        blank=True, default="", help_text="Sanitized failure description; never store credentials."
    )

    class Meta:
        """Database invariants for trustworthy synchronization checkpoints."""

        db_table = "github_repository_contribution_sync_states"
        verbose_name_plural = "Repository contribution sync states"
        constraints = [
            models.UniqueConstraint(
                fields=("repository", "contribution_type"), name="repo_contribution_sync_unique"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(covered_from__isnull=True, covered_until__isnull=True)
                    | models.Q(
                        covered_from__isnull=False,
                        covered_until__isnull=False,
                        covered_until__gte=models.F("covered_from"),
                    )
                ),
                name="repo_contribution_sync_coverage",
            ),
            models.CheckConstraint(
                condition=models.Q(contribution_type__in=("commits", "issues", "pull_requests")),
                name="repo_contribution_sync_type",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(default_branch="", last_head_sha="")
                    | models.Q(contribution_type="commits", last_head_sha="")
                    | models.Q(
                        contribution_type="commits",
                        default_branch__gt="",
                        covered_from__isnull=False,
                    )
                ),
                name="repo_contribution_sync_head",
            ),
        ]

    def __str__(self) -> str:
        """Identify the repository and category without requiring an owner."""
        return f"{self.repository.name}: {self.get_contribution_type_display()}"
