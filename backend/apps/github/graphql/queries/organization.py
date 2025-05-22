"""GitHub organization GraphQL queries."""

import strawberry

from apps.github.graphql.nodes.organization import OrganizationNode
from apps.github.models.organization import Organization


@strawberry.type
class OrganizationQuery:
    """Organization queries."""

    @strawberry.field
    def organization(
        self,
        info,
        *,
        login: str,
    ) -> OrganizationNode | None:
        """Resolve organization by login.

        Args:
            self: The OrganizationQuery instance.
            info: GraphQL execution context.
            login (str): The login of the organization.

        Returns:
            OrganizationNode: The organization node if found, otherwise None.

        """
        try:
            return Organization.objects.get(is_owasp_organization=True, login=login)
        except Organization.DoesNotExist:
            return None
