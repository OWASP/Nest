"""Github app organization model."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import GenericUserModel, NodeModel
from apps.github.models.managers.organization import RelatedOrganizationsManager
from apps.github.models.mixins import OrganizationIndexMixin

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models import QuerySet


class Organization(
    BulkSaveModel,
    NodeModel,
    GenericUserModel,
    OrganizationIndexMixin,
    TimestampedModel,
):
    """Organization model."""

    objects = models.Manager()
    related_organizations = RelatedOrganizationsManager()

    class Meta:
        db_table = "github_organizations"
        verbose_name_plural = "Organizations"

    description = models.CharField(
        verbose_name="Description", max_length=1000, blank=True, default=""
    )
    is_owasp_related_organization = models.BooleanField(
        verbose_name="Is OWASP related organization", default=True
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the organization.

        Returns
            str: The name of the organization.

        """
        return self.name

    @property
    def related_projects(self) -> QuerySet:
        """Return organization related projects."""
        return (
            apps.get_model("owasp", "Project")  # Dynamic import.
            .objects.select_related("owasp_repository")
            .prefetch_related("organizations", "owners", "repositories")
            .filter(
                repositories__in=self.repositories.all(),
            )
            .distinct()
        )

    def from_github(self, gh_organization) -> None:
        """Update the instance based on GitHub organization data.

        Args:
            gh_organization (github.Organization.Organization): The GitHub organization object.

        """
        super().from_github(gh_organization)

        field_mapping = {
            "description": "description",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_organization, gh_field)
            if value is not None:
                setattr(self, model_field, value)

    @lru_cache
    @staticmethod
    def get_logins():
        """Retrieve all organization logins."""
        return set(Organization.objects.values_list("login", flat=True))

    @staticmethod
    def bulk_save(organizations, fields=None) -> None:  # type: ignore[override]
        """Bulk save organizations."""
        BulkSaveModel.bulk_save(Organization, organizations, fields=fields)

    @staticmethod
    def update_data(gh_organization, *, save: bool = True) -> Organization:
        """Update organization data.

        Args:
            gh_organization (github.Organization.Organization): The GitHub organization object.
            save (bool, optional): Whether to save the instance.

        Returns:
            Organization: The updated or created organization instance.

        """
        organization_node_id = Organization.get_node_id(gh_organization)
        try:
            organization = Organization.objects.get(node_id=organization_node_id)
        except Organization.DoesNotExist:
            organization = Organization(node_id=organization_node_id)

        organization.from_github(gh_organization)
        if save:
            organization.save()

        return organization
