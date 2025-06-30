"""OWASP app organization managers."""

from django.db import models

from apps.owasp.constants import OWASP_ORGANIZATION_NAME


class RelatedOrganizationsManager(models.Manager):
    """OWASP related organizations manager."""

    def get_queryset(self):
        """Get open milestones."""
        return (
            super()
            .get_queryset()
            .filter(
                is_owasp_related_organization=True,
            )
            .exclude(login=OWASP_ORGANIZATION_NAME)
        )
