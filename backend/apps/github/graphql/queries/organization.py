"""GitHub organization GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.organization import OrganizationNode
from apps.github.models.organization import Organization


class OrganizationQuery(BaseQuery):
    """Organization queries."""

    organization = graphene.Field(
        OrganizationNode,
        login=graphene.String(required=True),
    )

    organizations = graphene.List(
        OrganizationNode,
        search=graphene.String(),
        limit=graphene.Int(default_value=6),
        offset=graphene.Int(default_value=0),
        order_by=graphene.String(default_value="-followers_count"),
    )

    def resolve_organization(root, info, login):
        """Resolve organization by login.

        Args:
            root: The root object.
            info: GraphQL execution info.
            login (str): The login of the organization.

        Returns:
            Organization: The organization object if found, otherwise None.

        """
        try:
            return Organization.objects.get(login=login)
        except Organization.DoesNotExist:
            return None