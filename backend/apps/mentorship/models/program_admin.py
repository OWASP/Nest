"""Program admin model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel


class ProgramAdmin(TimestampedModel):
    """Program admin relationship with role."""

    class AdminRole(models.TextChoices):
        OWNER = "owner", "Owner"

    class Meta:
        db_table = "mentorship_program_admins"
        verbose_name_plural = "Program admins"
        unique_together = ("program", "user")

    # FKs.
    program = models.ForeignKey(
        "mentorship.Program",
        on_delete=models.CASCADE,
        verbose_name="Program",
        related_name="program_admins",
    )

    user = models.ForeignKey(
        "nest.User",
        on_delete=models.CASCADE,
        verbose_name="User",
        related_name="program_admin_roles",
    )

    role = models.CharField(
        max_length=20,
        choices=AdminRole.choices,
        default=AdminRole.OWNER,
        verbose_name="Role",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the program admin.

        Returns:
            str: User and program with role.

        """
        return f"{self.user} - {self.program} ({self.role})"
