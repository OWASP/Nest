"""Mentorship app linked user."""

from django.db import models


class LinkedUser(models.Model):
    """Linked user model connecting nest.User and github.User."""

    class Meta:
        """Model options."""

        abstract = True

    # FKs.
    github_user = models.OneToOneField(
        "github.User",
        on_delete=models.CASCADE,
        verbose_name="GitHub user",
        related_name="%(class)s_github_user",
    )

    nest_user = models.OneToOneField(
        "nest.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Nest user",
        related_name="%(class)s_nest_user",
    )
