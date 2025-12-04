"""OWASP app organization managers."""

from django.db import models
from django.db.models import Q

from apps.owasp.constants import OWASP_ORGANIZATION_NAME


class RelatedOrganizationsManager(models.Manager):
    """OWASP related organizations manager."""

    def get_queryset(self) -> models.QuerySet:
        """Get OWASP related organizations."""
        return (
            super()
            .get_queryset()
            .exclude(
                Q(login=OWASP_ORGANIZATION_NAME) | Q(is_owasp_related_organization=False),
            )
        )
