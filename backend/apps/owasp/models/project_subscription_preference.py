"""OWASP app project subscription preference model."""

from django.db import models


class ProjectSubscriptionPreference(models.Model):
    """Per-project content preferences for a snapshot subscription."""

    class Meta:
        """Model options."""

        db_table = "owasp_project_subscription_preferences"
        verbose_name_plural = "Project Subscription Preferences"
        constraints = [
            models.UniqueConstraint(
                fields=["subscription", "project"],
                name="unique_subscription_project",
            ),
        ]

    subscription = models.ForeignKey(
        "owasp.SnapshotSubscription",
        on_delete=models.CASCADE,
        related_name="project_preferences",
    )
    project = models.ForeignKey(
        "owasp.Project",
        on_delete=models.CASCADE,
        related_name="subscription_preferences",
    )

    # Per-project toggles
    include_issues = models.BooleanField(default=True)
    include_pull_requests = models.BooleanField(default=True)
    include_releases = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation."""
        return str(self.project)
