"""ProgramModule model for the Mentorship app."""

from __future__ import annotations

from django.db import models


class ProgramModule(models.Model):
    """Join table linking Program and Module with optional custom start/end dates."""

    class Meta:
        db_table = "mentorship_program_modules"
        unique_together = ("program", "module")
        verbose_name = "Program module link"
        verbose_name_plural = "Program module links"

    end_date = models.DateField(
        verbose_name="End date",
        blank=True,
        help_text="Defaults to the program's end date if not specified.",
    )

    start_date = models.DateField(
        verbose_name="Start date",
        blank=True,
        help_text="Defaults to the program's start date if not specified.",
    )

    # FKs.
    module = models.OneToOneField(
        "mentorship.Module",
        on_delete=models.CASCADE,
        verbose_name="Module",
    )

    program = models.ForeignKey(
        "mentorship.Program",
        on_delete=models.CASCADE,
        verbose_name="Program",
    )

    def save(self, *args, **kwargs):
        """Save program module."""
        if self.program:
            # Set default dates from program if not provided.
            self.start_date = self.start_date or self.program.start_date
            self.end_date = self.end_date or self.program.end_date

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a readable identifier for the program module link."""
        return f"{self.module.name} of {self.program.name}"
