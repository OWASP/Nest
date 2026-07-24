"""OWASP app entity subscription model."""

import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.nest.models import User
from apps.owasp.models.entity_subscription_preference import EntitySubscriptionPreference

MAX_ENTITY_SUBSCRIPTIONS = 5


class EntitySubscription(models.Model):
    """Model representing a user's entity-specific subscription to snapshot digest emails."""

    class Meta:
        """Model options."""

        db_table = "owasp_entity_subscriptions"
        verbose_name_plural = "Entity Subscriptions"
        indexes = [
            models.Index(fields=["is_active"], name="owasp_entity_sub_active_idx"),
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
    name = models.CharField(max_length=100, blank=True, default="")
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation."""
        status = (
            EntitySubscription.Status.ACTIVE
            if self.is_active
            else EntitySubscription.Status.INACTIVE
        )
        return f"{self.user} ({self.name}, {self.frequency}, {status})"

    def clean(self):
        """Validate the model before saving."""
        super().clean()

        if self.is_active and getattr(self, "user_id", None):
            query = EntitySubscription.objects.filter(user=self.user, is_active=True)
            if self.pk:
                query = query.exclude(pk=self.pk)

            if query.count() >= MAX_ENTITY_SUBSCRIPTIONS:
                msg = "Maximum number of entity subscriptions reached."
                raise ValidationError(msg)

    @classmethod
    @transaction.atomic
    def create(cls, *, user, frequency, **kwargs):
        """Create a new entity subscription with limit enforcement.

        Args:
            user: The user creating the subscription.
            frequency: "weekly" or "monthly".
            **kwargs: Additional fields (name).

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

        return cls.objects.create(
            user=user,
            frequency=frequency,
            **kwargs,
        )

    def update(self, *, frequency=None, **kwargs):
        """Update subscription fields.

        Args:
            frequency: New frequency value, if changing.
            **kwargs: Additional fields to update.

        """
        if frequency is not None:
            self.frequency = frequency

        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)

        self.full_clean()
        self.save()

    @transaction.atomic
    def sync_preferences(self, preferences_data):
        """Sync entity preferences using a diff-based approach.

        Instead of delete-all-and-recreate, this method:
        - Creates new preferences that don't exist yet.
        - Updates existing preferences that changed.
        - Removes preferences no longer in the input.

        Args:
            preferences_data: List of dicts with entity info and toggles.
                Each dict must have: entity_type, entity_id,
                include_issues, include_pull_requests, include_releases.

        """
        existing = {self._preference_key(pref): pref for pref in self.entity_preferences.all()}

        incoming_keys = set()
        for data in preferences_data:
            key = (data["entity_type"], data["entity_id"])
            incoming_keys.add(key)

            fk_field = data["entity_type"]
            fk_kwargs = {f"{fk_field}_id": data["entity_id"]}
            toggle_fields = {
                "include_issues": data.get("include_issues", True),
                "include_pull_requests": data.get("include_pull_requests", True),
                "include_releases": data.get("include_releases", True),
            }

            if key in existing:
                pref = existing[key]
                changed = False
                for field, value in toggle_fields.items():
                    if getattr(pref, field) != value:
                        setattr(pref, field, value)
                        changed = True
                if changed:
                    pref.save()
            else:
                EntitySubscriptionPreference.objects.create(
                    subscription=self,
                    **fk_kwargs,
                    **toggle_fields,
                )

        # Remove preferences no longer in the input.
        for key, pref in existing.items():
            if key not in incoming_keys:
                pref.delete()

    @staticmethod
    def _preference_key(pref):
        """Return a (entity_type, entity_id) tuple for a preference."""
        if pref.project_id:
            return ("project", pref.project_id)
        if pref.chapter_id:
            return ("chapter", pref.chapter_id)
        if pref.committee_id:
            return ("committee", pref.committee_id)
        return (None, None)
