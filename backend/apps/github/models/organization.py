"""Github app organization model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import GenericUserModel, NodeModel
from apps.github.models.mixins import OrganizationIndexMixin


class Organization(
    BulkSaveModel,
    NodeModel,
    GenericUserModel,
    OrganizationIndexMixin,
    TimestampedModel,
):
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
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_organization, gh_field)
            if value is not None:
                setattr(self, model_field, value)

    @staticmethod
    def bulk_save(organizations):
        """Bulk save organizations."""
        BulkSaveModel.bulk_save(Organization, organizations)

    @staticmethod
    def update_data(gh_organization, save=True):
        """Update organization data."""
        organization_node_id = Organization.get_node_id(gh_organization)
        try:
            organization = Organization.objects.get(node_id=organization_node_id)
        except Organization.DoesNotExist:
            organization = Organization(node_id=organization_node_id)

        organization.from_github(gh_organization)
        if save:
            organization.save()

        return organization
