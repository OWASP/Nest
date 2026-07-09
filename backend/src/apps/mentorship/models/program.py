"""Program model for the Mentorship app."""

from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q

from apps.common.models import TimestampedModel
from apps.common.utils import slugify
from apps.mentorship.models.common import (
    ExperienceLevel,
    MatchingAttributes,
    StartEndRange,
)
from apps.mentorship.models.mixins.program import ProgramIndexMixin


class Program(MatchingAttributes, ProgramIndexMixin, StartEndRange, TimestampedModel):
    """Program model representing an overarching mentorship initiative."""

    class Meta:
        """Model options."""

        db_table = "mentorship_programs"
        verbose_name_plural = "Programs"

    class ProgramStatus(models.TextChoices):
        """Program lifecycle status choices."""

        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        COMPLETED = "completed", "Completed"

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
    )

    experience_levels = ArrayField(
        base_field=models.CharField(
            max_length=12,
            choices=ExperienceLevel.ExperienceLevelChoices.choices,
        ),
        blank=True,
        default=list,
        verbose_name="Experience levels",
    )

    mentees_limit = models.PositiveIntegerField(
        verbose_name="Mentees limit",
        blank=True,
        null=True,
        help_text="Maximum number of mentees allowed in this program",
    )

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Name",
    )
    key = models.CharField(verbose_name="Key", max_length=200, unique=True)

    status = models.CharField(
        verbose_name="Status",
        max_length=9,
        choices=ProgramStatus.choices,
        default=ProgramStatus.DRAFT,
    )

    # M2Ms.
    admins = models.ManyToManyField(
        "mentorship.Admin",
        through="mentorship.ProgramAdmin",
        related_name="admin_programs",
        verbose_name="Admins",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the program.

        Returns:
            str: The program name.

        """
        return self.name

    def has_admin(self, user) -> bool:
        """Check if the given user is an admin of this program.

        Falls back to a github_user lookup for admins who have not linked
        their nest_user profile yet.
        """
        if not user.is_authenticated:
            return False

        query = Q(nest_user=user)
        github_user = getattr(user, "github_user", None)
        if github_user is not None:
            query |= Q(github_user=github_user)

        return self.admins.filter(query).exists()

    def user_has_access(self, user) -> bool:
        """Check if the given user has any role (admin, mentor, or mentee) here.

        Returns True if the user is authenticated and is an admin, mentor, or
        mentee of this program, False otherwise.
        """
        return self.get_user_role(user) is not None

    def get_user_role(self, user) -> str | None:
        """Return the user's highest role in this program.

        One of "admin", "mentor", or "mentee", or None if the user is not
        authenticated or has no role in the program. Admin takes precedence over
        mentor, and mentor over mentee.
        """
        if not user.is_authenticated:
            return None

        if self.has_admin(user):
            return "admin"

        github_user = getattr(user, "github_user", None)

        mentor_q = Q(mentors__nest_user=user)
        mentee_q = Q(menteemodule__mentee__nest_user=user)
        if github_user is not None:
            mentor_q |= Q(mentors__github_user=github_user)
            mentee_q |= Q(menteemodule__mentee__github_user=github_user)

        if self.modules.filter(mentor_q).exists():
            return "mentor"
        if self.modules.filter(mentee_q).exists():
            return "mentee"
        return None

    def save(self, *args, **kwargs) -> None:
        """Save program."""
        self.key = slugify(self.name)

        super().save(*args, **kwargs)
