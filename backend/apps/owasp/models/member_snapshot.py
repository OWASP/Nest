"""OWASP app member snapshot model."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models.user import User


class MemberSnapshot(TimestampedModel):
    """OWASP Member Snapshot model.

    Tracks aggregated contribution statistics for a GitHub user over a time period.
    """

    class Meta:
        db_table = "owasp_member_snapshots"
        verbose_name_plural = "Member Snapshots"
        unique_together = ("github_user", "start_at", "end_at")

    chapter_contributions = models.JSONField(
        verbose_name="Chapter Contributions",
        default=dict,
        blank=True,
        help_text="Contribution counts per chapter (chapter_key -> count mapping)",
    )
    contribution_heatmap_data = models.JSONField(
        verbose_name="Contribution Heatmap Data",
        default=dict,
        blank=True,
        help_text="Daily contribution counts (YYYY-MM-DD -> count mapping)",
    )
    project_contributions = models.JSONField(
        verbose_name="Project Contributions",
        default=dict,
        blank=True,
        help_text="Contribution counts per project (project_key -> count mapping)",
    )
    github_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contribution_snapshots",
        help_text="GitHub user for this snapshot",
    )
    start_at = models.DateTimeField(
        verbose_name="Start Date",
        help_text="Start of the snapshot period",
    )
    end_at = models.DateTimeField(
        verbose_name="End Date",
        help_text="End of the snapshot period",
    )

    # M2Ms.
    commits = models.ManyToManyField(
        "github.Commit",
        verbose_name="Commits",
        related_name="member_snapshots",
        blank=True,
        help_text="Commits authored by the user during this period",
    )
    issues = models.ManyToManyField(
        "github.Issue",
        verbose_name="Issues",
        related_name="member_snapshots",
        blank=True,
        help_text="Issues created by the user during this period",
    )
    pull_requests = models.ManyToManyField(
        "github.PullRequest",
        verbose_name="Pull Requests",
        related_name="member_snapshots",
        blank=True,
        help_text="Pull requests created by the user during this period",
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return (
            f"{self.github_user.login} snapshot ({self.start_at.date()} to {self.end_at.date()})"
        )

    @property
    def commits_count(self) -> int:
        """Return the number of commits in this snapshot."""
        return self.commits.count()

    @property
    def pull_requests_count(self) -> int:
        """Return the number of pull requests in this snapshot."""
        return self.pull_requests.count()

    @property
    def issues_count(self) -> int:
        """Return the number of issues in this snapshot."""
        return self.issues.count()

    @property
    def total_contributions(self) -> int:
        """Return the total number of contributions in this snapshot."""
        return self.commits_count + self.pull_requests_count + self.issues_count
