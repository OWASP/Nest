"""Participant interest model."""

from django.db import models


class ContributorInterest(models.Model):
    """Represents users interested in a specific issue within a module."""

    module = models.ForeignKey(
        "mentorship.Module", on_delete=models.CASCADE, related_name="interests"
    )
    issue = models.ForeignKey(
        "github.Issue", on_delete=models.CASCADE, related_name="participant_interests"
    )
    users = models.ManyToManyField("github.User", related_name="mentorship_interests", blank=True)

    class Meta:
        unique_together = ("module", "issue")
        verbose_name_plural = "Contributor Interests"

    def __str__(self):
        """Return a human-readable representation of the contributor interest."""
        user_list = ", ".join(self.users.values_list("login", flat=True))
        return f"Users [{user_list}] interested in '{self.issue.title}' for {self.module.name}"
