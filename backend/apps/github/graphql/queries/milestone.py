"""Github Milestone Queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.milestone import MilestoneNode
from apps.github.models.milestone import Milestone


class MilestoneQuery(BaseQuery):
    """Github Milestone Queries."""

    open_milestones = graphene.List(
        MilestoneNode,
        limit=graphene.Int(default_value=5),
        login=graphene.String(required=False),
        organization=graphene.String(required=False),
        distinct=graphene.Boolean(default_value=False),
    )

    closed_milestones = graphene.List(
        MilestoneNode,
        limit=graphene.Int(default_value=5),
        login=graphene.String(required=False),
        organization=graphene.String(required=False),
        distinct=graphene.Boolean(default_value=False),
    )

    def resolve_open_milestones(root, info, limit, login=None, organization=None, distinct=False):
        """Resolve open milestones.

        Args:
            root (object): The root object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): The maximum number of milestones to return.
            login (str, optional): Filter milestones by author login.
            organization (str, optional): Filter milestones by organization login.
            distinct (bool, optional): Whether to return distinct milestones.

        Returns:
            list: A list of open milestones.

        """
        open_milestones = Milestone.open_milestones.select_related(
            "author",
            "repository",
            "repository__organization",
        )

        if login:
            open_milestones = open_milestones.filter(author__login=login)
        if organization:
            open_milestones = open_milestones.filter(repository__organization__login=organization)

        return open_milestones[:limit]

    def resolve_closed_milestones(
        root, info, limit, login=None, organization=None, distinct=False
    ):
        """Resolve closed milestones.

        Args:
            root (object): The root object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): The maximum number of milestones to return.
            login (str, optional): Filter milestones by author login.
            organization (str, optional): Filter milestones by organization login.
            distinct (bool, optional): Whether to return distinct milestones.

        Returns:
            list: A list of closed milestones.

        """
        closed_milestones = Milestone.closed_milestones.select_related(
            "author",
            "repository",
            "repository__organization",
        )

        if login:
            closed_milestones = closed_milestones.filter(author__login=login)
        if organization:
            closed_milestones = closed_milestones.filter(
                repository__organization__login=organization
            )

        return closed_milestones[:limit]
