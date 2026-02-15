"""GitHub organization GraphQL queries."""

import strawberry

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.organization import OrganizationNode
from apps.github.models.organization import Organization

MAX_LIMIT = 100


@strawberry.type
class OrganizationQuery:
    """Organization queries."""

    @strawberry.field
    def organization(
        self,
        *,
        login: str,
    ) -> OrganizationNode | None:
        """Resolve organization by login.

        Args:
            login (str): The login of the organization.

        Returns:
            OrganizationNode: The organization node if found, otherwise None.

        """
        try:
            return Organization.objects.get(is_owasp_related_organization=True, login=login)
        except Organization.DoesNotExist:
            return None

    @strawberry.field
    def recent_organizations(self, limit: int = 5) -> list[OrganizationNode]:
        """Resolve recent organizations.

        Args:
            limit (int): The number of recent organizations to return.

        Returns:
            list: A list of recent organization.

        """
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return Organization.objects.filter(is_owasp_related_organization=True).order_by(
            "-created_at"
        )[:normalized_limit]
