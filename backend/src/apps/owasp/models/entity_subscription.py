"""OWASP app entity subscription model."""

import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.nest.models import User

MAX_ENTITY_SUBSCRIPTIONS = 5


class EntitySubscription(models.Model):
    """Model representing a user's subscription to a single entity's digest emails.

    Each subscription maps to exactly one entity (project, chapter, or committee)
    with its own frequency. Subscribing to an entity means receiving all updates
    related to it.
    """

    class Meta:
        """Model options."""

        db_table = "owasp_entity_subscriptions"
        verbose_name_plural = "Entity Subscriptions"
        indexes = [
            models.Index(fields=["is_active"], name="owasp_entity_sub_active_idx"),
        ]
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
                name="entity_sub_exactly_one_entity",
            ),
            models.UniqueConstraint(
                fields=("user", "project"),
                condition=models.Q(project__isnull=False),
                name="unique_user_project_subscription",
            ),
            models.UniqueConstraint(
                fields=("user", "chapter"),
                condition=models.Q(chapter__isnull=False),
                name="unique_user_chapter_subscription",
            ),
            models.UniqueConstraint(
                fields=("user", "committee"),
                condition=models.Q(committee__isnull=False),
                name="unique_user_committee_subscription",
            ),
        ]

    class Frequency(models.TextChoices):
        """Subscription frequency choices."""

        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    class Status(models.TextChoices):
        """Subscription status choices."""

        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="entity_subscriptions",
    )
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    chapter = models.ForeignKey(
        "owasp.Chapter",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="entity_subscriptions",
    )
    committee = models.ForeignKey(
        "owasp.Committee",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="entity_subscriptions",
    )
    project = models.ForeignKey(
        "owasp.Project",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="entity_subscriptions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation."""
        status = (
            EntitySubscription.Status.ACTIVE
            if self.is_active
            else EntitySubscription.Status.INACTIVE
        )
        return f"{self.user} → {self.entity} ({self.frequency}, {status})"

    @property
    def entity(self):
        """Return the associated entity (project, chapter, or committee)."""
        return self.chapter or self.committee or self.project

    @property
    def entity_type(self):
        """Return the entity type string."""
        if self.chapter_id:
            return "chapter"
        if self.committee_id:
            return "committee"
        if self.project_id:
            return "project"
        return None

    def clean(self):
        """Validate the model before saving."""
        super().clean()

        entity_count = sum(
            [
                self.project_id is not None,
                self.chapter_id is not None,
                self.committee_id is not None,
            ]
        )
        if entity_count == 0:
            msg = "You must select exactly one project, chapter, or committee."
            raise ValidationError(msg)
        if entity_count > 1:
            msg = (
                "You can only subscribe to one entity per subscription."
                " Please select only one project, chapter, or committee."
            )
            raise ValidationError(msg)

        if getattr(self, "user_id", None):
            for field in ("chapter", "committee", "project"):
                entity_id = getattr(self, f"{field}_id", None)
                if entity_id is not None:
                    query = EntitySubscription.objects.filter(
                        user=self.user, **{f"{field}_id": entity_id}
                    )
                    if self.pk:
                        query = query.exclude(pk=self.pk)
                    if query.exists():
                        msg = "You are already subscribed to this entity."
                        raise ValidationError(msg)

        if self.is_active and getattr(self, "user_id", None):
            query = EntitySubscription.objects.filter(user=self.user, is_active=True)
            if self.pk:
                query = query.exclude(pk=self.pk)

            if query.count() >= MAX_ENTITY_SUBSCRIPTIONS:
                msg = "Maximum number of entity subscriptions reached."
                raise ValidationError(msg)

    def validate_constraints(self, exclude=None):
        """Skip DB-level constraint validation.

        The entity-count and uniqueness checks are already handled in clean()
        with user-friendly messages, so we suppress the raw constraint errors.
        """

    @classmethod
    @transaction.atomic
    def create(cls, *, user, frequency, entity_type, entity_id):
        """Create a new entity subscription with limit enforcement.

        Args:
            user: The user creating the subscription.
            frequency: "weekly" or "monthly".
            entity_type: "project", "chapter", or "committee".
            entity_id: The ID of the entity.

        Returns:
            The created subscription instance, or None if limit reached.

        """
        if getattr(user, "pk", None):
            User.objects.select_for_update().filter(pk=user.pk).exists()

        active_count = cls.objects.filter(
            user=user,
            is_active=True,
        ).count()
        if active_count >= MAX_ENTITY_SUBSCRIPTIONS:
            return None

        fk_kwargs = {f"{entity_type}_id": entity_id}
        return cls.objects.create(
            user=user,
            frequency=frequency,
            **fk_kwargs,
        )

    def update(self, *, frequency=None):
        """Update subscription fields.

        Args:
            frequency: New frequency value, if changing.

        """
        if frequency is not None:
            self.frequency = frequency

        self.full_clean()
        self.save()
