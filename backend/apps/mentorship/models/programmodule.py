"""ProgramModule model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.mentorship.models.module import Module
from apps.mentorship.models.program import Program


class ProgramModule(models.Model):
    """Join table linking Program and Module with optional custom start/end dates."""

    class Meta:
        db_table = "mentorship_program_modules"
        unique_together = ("program", "module")
        verbose_name = "Program Module Link"
        verbose_name_plural = "Program Module Links"

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="program_modules",
        verbose_name="Associated program",
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="module_programs",
        verbose_name="Associated module",
    )

    start_date = models.DateField(
        verbose_name="Start date",
        null=True,
        blank=True,
        help_text="Defaults to the program's start date if not specified.",
    )

    end_date = models.DateField(
        verbose_name="End date",
        null=True,
        blank=True,
        help_text="Defaults to the program's end date if not specified.",
    )

    def save(self, *args, **kwargs):
        """Set default dates from program if not provided."""
        if self.program:
            self.start_date = self.start_date or self.program.start_date
        self.end_date = self.end_date or self.program.end_date
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a readable identifier for the Program-Module link."""
        return f"{self.module.name or 'Unnamed Module'} in {self.program.name}"
