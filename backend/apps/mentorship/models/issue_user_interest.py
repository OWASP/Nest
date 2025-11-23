"""Participant interest model."""

from django.db import models


class IssueUserInterest(models.Model):
    """Represents users interested in a specific issue within a module."""

    class Meta:
        db_table = "mentorship_issue_user_interests"
        verbose_name = "Issue User Interest"
        verbose_name_plural = "Issue User Interests"
        unique_together = ("module", "issue", "user")

    # FKs.
    issue = models.ForeignKey(
        "github.Issue",
        on_delete=models.CASCADE,
        related_name="participant_interests",
    )
    module = models.ForeignKey(
        "mentorship.Module",
        on_delete=models.CASCADE,
        related_name="interests",
    )
    user = models.ForeignKey(
        "github.User",
        related_name="mentorship_interests",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Return a human-readable representation of the issue user interest."""
        return (
            f"User [{self.user.login}] interested in '{self.issue.title}' for {self.module.name}"
        )
