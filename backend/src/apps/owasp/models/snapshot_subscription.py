"""OWASP app snapshot subscription model."""

import uuid

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction

from apps.nest.models import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project

MAX_SUBSCRIPTIONS = 5


class SnapshotSubscription(models.Model):
    """Model representing a user's subscription to snapshot digest emails.

    Each subscription is a named container that groups global OWASP content
    toggles and specific entity selections. A user can have up to 5
    subscriptions, each producing one digest email.
    """

    class Meta:
        """Model options."""

        db_table = "owasp_snapshot_subscriptions"
        verbose_name_plural = "Snapshot Subscriptions"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_user_subscription_name",
            ),
        ]
        indexes = [
            models.Index(fields=["is_active"], name="owasp_sub_active_idx"),
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
        related_name="snapshot_subscriptions",
    )
    name = models.CharField(max_length=100, default="", blank=True)
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

    # Content toggles.
    include_chapters = models.BooleanField(default=False)
    include_events = models.BooleanField(default=False)
    include_issues = models.BooleanField(default=False)
    include_posts = models.BooleanField(default=False)
    include_projects = models.BooleanField(default=False)
    include_pull_requests = models.BooleanField(default=False)
    include_releases = models.BooleanField(default=False)
    include_users = models.BooleanField(default=False)

    # Specific entity subscriptions.
    subscribed_projects = models.ManyToManyField(
        "owasp.Project",
        blank=True,
        related_name="snapshot_subscriptions",
    )
    subscribed_chapters = models.ManyToManyField(
        "owasp.Chapter",
        blank=True,
        related_name="snapshot_subscriptions",
    )
    subscribed_committees = models.ManyToManyField(
        "owasp.Committee",
        blank=True,
        related_name="snapshot_subscriptions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation."""
        status = (
            SnapshotSubscription.Status.ACTIVE
            if self.is_active
            else SnapshotSubscription.Status.INACTIVE
        )
        name = self.name or "Unnamed"
        return f"{self.user} — {name} ({self.frequency}, {status})"

    @property
    def content_preferences(self):
        """Return a dictionary of content preference settings."""
        return {
            "chapters": self.include_chapters,
            "events": self.include_events,
            "issues": self.include_issues,
            "posts": self.include_posts,
            "projects": self.include_projects,
            "pull_requests": self.include_pull_requests,
            "releases": self.include_releases,
            "users": self.include_users,
        }

    def clean(self):
        """Validate the model before saving."""
        super().clean()

        toggles = [
            self.include_chapters,
            self.include_events,
            self.include_issues,
            self.include_posts,
            self.include_projects,
            self.include_pull_requests,
            self.include_releases,
            self.include_users,
        ]
        has_entities = False
        if self.pk:
            has_entities = any(
                [
                    self.subscribed_projects.exists(),
                    self.subscribed_chapters.exists(),
                    self.subscribed_committees.exists(),
                ]
            )

        if not getattr(self, "_is_admin_form", False) and not any(toggles) and not has_entities:
            msg = "Your subscription cannot be empty. Please choose something to follow."
            raise ValidationError(msg)

        if self.is_active and getattr(self, "user_id", None):
            query = SnapshotSubscription.objects.filter(user=self.user, is_active=True)
            if self.pk:
                query = query.exclude(pk=self.pk)

            if query.count() >= MAX_SUBSCRIPTIONS:
                msg = f"Maximum number of subscriptions ({MAX_SUBSCRIPTIONS}) reached."
                raise ValidationError(msg)

    @classmethod
    @transaction.atomic
    def create(cls, *, user, frequency, name="", **kwargs):
        """Create a new snapshot subscription with limit enforcement.

        Args:
            user: The user creating the subscription.
            frequency: "weekly" or "monthly".
            name: User-defined subscription name.
            **kwargs: Additional fields (content toggles).

        Returns:
            The created subscription instance, or None if limit reached.

        """
        if getattr(user, "pk", None):
            User.objects.select_for_update().filter(pk=user.pk).exists()

        active_count = cls.objects.filter(
            user=user,
            is_active=True,
        ).count()
        if active_count >= MAX_SUBSCRIPTIONS:
            msg = f"Maximum number of subscriptions ({MAX_SUBSCRIPTIONS}) reached."
            raise ValidationError(msg)

        if not name:
            name = cls._generate_default_name(user)

        try:
            return cls.objects.create(
                user=user,
                frequency=frequency,
                name=name,
                **kwargs,
            )
        except IntegrityError as e:
            msg = "A subscription with this name already exists."
            raise ValidationError(msg) from e

    @classmethod
    def _generate_default_name(cls, user):
        """Generate a default subscription name like 'Subscription 1'.

        Finds the next available number by checking existing subscription names.

        Args:
            user: The user to generate the name for.

        Returns:
            str: A unique default name.

        """
        existing_names = set(cls.objects.filter(user=user).values_list("name", flat=True))
        counter = len(existing_names) + 1
        while f"Subscription {counter}" in existing_names:
            counter += 1
        return f"Subscription {counter}"

    def update(self, *, frequency=None, name=None, **kwargs):
        """Update subscription fields.

        Args:
            frequency: New frequency value, if changing.
            name: New subscription name, if changing.
            **kwargs: Additional fields to update.

        """
        if frequency is not None:
            self.frequency = frequency

        if name is not None:
            self.name = name

        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)

        self.save()

    def set_m2m_fields(self, *, project_ids=None, chapter_ids=None, committee_ids=None):
        """Set M2M entity fields on this subscription.

        Args:
            project_ids: List of project IDs, or None to skip.
            chapter_ids: List of chapter IDs, or None to skip.
            committee_ids: List of committee IDs, or None to skip.

        """
        if project_ids is not None:
            self.subscribed_projects.set(Project.objects.filter(pk__in=project_ids))

        if chapter_ids is not None:
            self.subscribed_chapters.set(Chapter.objects.filter(pk__in=chapter_ids))

        if committee_ids is not None:
            self.subscribed_committees.set(Committee.objects.filter(pk__in=committee_ids))

    def deactivate(self):
        """Deactivate this subscription."""
        self.is_active = False
        self.save(update_fields=("is_active",))

    @transaction.atomic
    def reactivate(self):
        """Reactivate an inactive subscription with limit enforcement.

        Raises:
            ValidationError: If already active or max subscriptions reached.

        """
        if self.is_active:
            msg = "Subscription is already active."
            raise ValidationError(msg)

        if getattr(self.user, "pk", None):
            User.objects.select_for_update().filter(pk=self.user.pk).exists()

        active_count = SnapshotSubscription.objects.filter(
            user=self.user,
            is_active=True,
        ).count()
        if active_count >= MAX_SUBSCRIPTIONS:
            msg = f"Maximum number of active subscriptions ({MAX_SUBSCRIPTIONS}) reached."
            raise ValidationError(msg)

        self.is_active = True
        self.save(update_fields=("is_active",))

    @classmethod
    def check_duplicate_setup(
        cls,
        *,
        user,
        frequency,
        include_chapters,
        include_events,
        include_issues,
        include_posts,
        include_projects,
        include_pull_requests,
        include_releases,
        include_users,
        entity_ids,
        exclude_pk=None,
    ):
        """Check if another subscription has the exact same setup.

        Compares frequency, all toggle values, and M2M entity sets.

        Returns:
            bool: True if a duplicate setup exists.

        """
        other_subs = cls.objects.filter(
            user=user,
            frequency=frequency,
            include_chapters=include_chapters,
            include_events=include_events,
            include_issues=include_issues,
            include_posts=include_posts,
            include_projects=include_projects,
            include_pull_requests=include_pull_requests,
            include_releases=include_releases,
            include_users=include_users,
        ).prefetch_related(
            "subscribed_projects",
            "subscribed_chapters",
            "subscribed_committees",
        )

        if exclude_pk is not None:
            other_subs = other_subs.exclude(pk=exclude_pk)

        if not other_subs.exists():
            return False

        current_project_ids = set(entity_ids.get("projects", []))
        current_chapter_ids = set(entity_ids.get("chapters", []))
        current_committee_ids = set(entity_ids.get("committees", []))

        return any(
            {p.pk for p in other.subscribed_projects.all()} == current_project_ids
            and {c.pk for c in other.subscribed_chapters.all()} == current_chapter_ids
            and {c.pk for c in other.subscribed_committees.all()} == current_committee_ids
            for other in other_subs
        )

    def has_duplicate_setup(self):
        """Check if another subscription has the exact same setup.

        Compares frequency, all toggle values, and M2M entity sets.

        Returns:
            bool: True if a duplicate setup exists.

        """
        return self.check_duplicate_setup(
            user=self.user,
            frequency=self.frequency,
            include_chapters=self.include_chapters,
            include_events=self.include_events,
            include_issues=self.include_issues,
            include_posts=self.include_posts,
            include_projects=self.include_projects,
            include_pull_requests=self.include_pull_requests,
            include_releases=self.include_releases,
            include_users=self.include_users,
            entity_ids={
                "projects": self.subscribed_projects.values_list("pk", flat=True),
                "chapters": self.subscribed_chapters.values_list("pk", flat=True),
                "committees": self.subscribed_committees.values_list("pk", flat=True),
            },
            exclude_pk=self.pk,
        )

    def validate_unique_setup(self):
        """Raise ValidationError if another subscription has the exact same setup.

        Raises:
            ValidationError: If a duplicate setup exists.

        """
        if self.has_duplicate_setup():
            msg = "A subscription with the same setup already exists."
            raise ValidationError(msg)
