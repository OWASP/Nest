"""Github app Organization model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models.common import GenericUserModel


class Organization(GenericUserModel, TimestampedModel):
    """Organization model."""

    class Meta:
        db_table = "github_organizations"
        verbose_name_plural = "Organizations"

    description = models.CharField(verbose_name="Description", max_length=1000, default="")

    def __str__(self):
        """Organization human readable representation."""
        return f"{self.name}"

    def from_github(self, gh_organization):
        """Update instance based on GitHub organization data."""
        super().from_github(gh_organization)

        field_mapping = {
            "description": "description",
        }

        # Direct fields.
        for model_field, response_field in field_mapping.items():
            value = getattr(gh_organization, response_field)
            if value is not None:
                setattr(self, model_field, value)
