"""Module model for the Mentorship app."""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from apps.common.models import TimestampedModel
from apps.common.utils import slugify
from apps.mentorship.models.common import (
    ExperienceLevel,
    MatchingAttributes,
    StartEndRange,
)
from apps.mentorship.models.managers import PublishedModuleManager


class Module(ExperienceLevel, MatchingAttributes, StartEndRange, TimestampedModel):
    """Module model representing a program unit."""

    objects = models.Manager()
    published_modules = PublishedModuleManager()

    class Meta:
        """Model options."""

        db_table = "mentorship_modules"
        ordering = ["order", "started_at"]
        verbose_name_plural = "Modules"
        constraints = [
            models.UniqueConstraint(
                fields=["program", "key"],
                name="unique_module_key_in_program",
            )
        ]

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
    )
    key = models.CharField(
        verbose_name="Key",
        max_length=200,
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        blank=True,
        default="",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Order",
        help_text="Display order of the module within its program.",
    )
    mentees_can_manage_deadlines = models.BooleanField(
        default=False,
        verbose_name="Mentees can manage deadlines",
        help_text=(
            "If enabled, mentees can set or update deadlines for issues "
            "assigned to them in this module."
        ),
    )

    # FKs.
    labels = models.JSONField(
        blank=True,
        default=list,
        verbose_name="Labels",
    )
    program = models.ForeignKey(
        "mentorship.Program",
        related_name="modules",
        on_delete=models.CASCADE,
        verbose_name="Program",
    )
    project = models.ForeignKey(
        "owasp.Project",
        on_delete=models.CASCADE,
        verbose_name="Project",
    )

    # M2Ms.
    issues = models.ManyToManyField(
        "github.Issue",
        verbose_name="Linked Issues",
        related_name="mentorship_modules",
        blank=True,
        help_text="Issues linked to this module via label matching.",
    )
    mentors = models.ManyToManyField(
        "mentorship.Mentor",
        verbose_name="Mentors",
        related_name="modules",
        through="mentorship.MentorModule",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the module.

        Returns:
            str: The module name or associated project.

        """
        return self.name

    def has_mentor(self, user) -> bool:
        """Check if the given user is a mentor of this module.

        Falls back to a github_user lookup for mentors who have not linked
        their nest_user profile yet.
        """
        if not user.is_authenticated:
            return False

        query = Q(nest_user=user)
        github_user = getattr(user, "github_user", None)
        if github_user is not None:
            query |= Q(github_user=github_user)

        return self.mentors.filter(query).exists()

    def has_mentee(self, user) -> bool:
        """Check if the given user is a mentee enrolled in this module.

        Falls back to a github_user lookup for mentees who have not linked
        their nest_user profile yet.
        """
        if not user.is_authenticated:
            return False

        query = Q(mentee__nest_user=user)
        github_user = getattr(user, "github_user", None)
        if github_user is not None:
            query |= Q(mentee__github_user=github_user)

        return self.menteemodule_set.filter(query).exists()

    def save(self, *args, **kwargs):
        """Save module."""
        if self.program:
            self.started_at = self.started_at or self.program.started_at
            self.ended_at = self.ended_at or self.program.ended_at

        if not self.pk and self.program:
            max_order = (
                Module.objects.filter(program=self.program)
                .aggregate(max_order=models.Max("order"))
                .get("max_order")
            )
            self.order = (max_order or 0) + 1

        self.key = slugify(self.name)
        super().save(*args, **kwargs)
