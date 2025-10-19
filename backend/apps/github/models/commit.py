"""Github app commit model."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import NodeModel


class Commit(BulkSaveModel, NodeModel, TimestampedModel):
    """Commit model."""

    class Meta:
        db_table = "github_commits"
        indexes = [
            models.Index(fields=["-created_at"], name="commit_created_at_desc_idx"),
            models.Index(fields=["sha"], name="commit_sha_idx"),
        ]
        verbose_name_plural = "Commits"

    created_at = models.DateTimeField(
        verbose_name="Created At",
        help_text="When the commit was created",
    )
    message = models.TextField(
        verbose_name="Commit Message",
        help_text="The commit message",
    )
    sha = models.CharField(
        verbose_name="SHA",
        max_length=64,
        help_text="Git commit SHA hash",
    )

    # FKs.
    repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.CASCADE,
        related_name="commits",
        help_text="Repository containing this commit",
    )
    author = models.ForeignKey(
        "github.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_commits",
        help_text="User who authored the commit",
    )
    committer = models.ForeignKey(
        "github.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="committed_commits",
        help_text="User who committed the commit",
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        short_sha = self.sha[:7] if self.sha else "unknown"
        message_preview = self.message[:100] if self.message else "No message"
        return f"{short_sha}: {message_preview}"

    @staticmethod
    def bulk_save(commits, fields=None) -> None:  # type: ignore[override]
        """Bulk save commits.

        Args:
            commits (list[Commit]): List of Commit instances to save.
            fields (tuple[str], optional): Tuple of fields to update.

        """
        BulkSaveModel.bulk_save(Commit, commits, fields=fields)

    @staticmethod
    def update_data(
        gh_commit, repository, author=None, committer=None, *, save: bool = True
    ) -> Commit:
        """Update commit data from GitHub commit object.

        Args:
            gh_commit: GitHub commit object.
            repository: Repository instance.
            author: User instance for commit author (optional).
            committer: User instance for committer (optional).
            save: Whether to save the instance.

        Returns:
            Commit: The updated or created commit instance.

        """
        node_id = gh_commit.raw_data.get("node_id", f"C_{gh_commit.sha}")

        try:
            commit = Commit.objects.get(node_id=node_id)
        except Commit.DoesNotExist:
            commit = Commit(node_id=node_id)

        commit.sha = gh_commit.sha
        commit.message = gh_commit.commit.message
        commit.created_at = gh_commit.commit.author.date
        commit.repository = repository
        commit.author = author
        commit.committer = committer

        if save:
            commit.save()

        return commit
