"""OWASP app entity subscription preference model."""

from django.db import models


class EntitySubscriptionPreference(models.Model):
    """Unified per-entity content preferences for an entity subscription.

    Supports projects, chapters, and committees. Exactly one entity
    foreign key must be set per preference instance, enforced via a
    database-level check constraint.
    """

    class Meta:
        """Model options."""

        db_table = "owasp_entity_subscription_preferences"
        verbose_name_plural = "Entity Subscription Preferences"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        project__isnull=False,
                        chapter__isnull=True,
                        committee__isnull=True,
                    )
                    | models.Q(
                        project__isnull=True,
                        chapter__isnull=False,
                        committee__isnull=True,
                    )
                    | models.Q(
                        project__isnull=True,
                        chapter__isnull=True,
                        committee__isnull=False,
                    )
                ),
                name="exactly_one_entity_set",
            ),
            models.UniqueConstraint(
                fields=["subscription", "project"],
                condition=models.Q(project__isnull=False),
                name="unique_subscription_project",
            ),
            models.UniqueConstraint(
                fields=["subscription", "chapter"],
                condition=models.Q(chapter__isnull=False),
                name="unique_subscription_chapter",
            ),
            models.UniqueConstraint(
                fields=["subscription", "committee"],
                condition=models.Q(committee__isnull=False),
                name="unique_subscription_committee",
            ),
        ]

    subscription = models.ForeignKey(
        "owasp.EntitySubscription",
        on_delete=models.CASCADE,
        related_name="entity_preferences",
    )

    chapter = models.ForeignKey(
        "owasp.Chapter",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="entity_subscription_preferences",
    )
    committee = models.ForeignKey(
        "owasp.Committee",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="entity_subscription_preferences",
    )
    project = models.ForeignKey(
        "owasp.Project",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="entity_subscription_preferences",
    )

    include_issues = models.BooleanField(default=True)
    include_pull_requests = models.BooleanField(default=True)
    include_releases = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation."""
        return str(self.entity)

    @property
    def entity(self):
        """Return the associated entity (project, chapter, or committee)."""
        return self.chapter or self.committee or self.project
