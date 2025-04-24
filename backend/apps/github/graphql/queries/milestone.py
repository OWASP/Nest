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
        project=graphene.String(required=False),
        repository=graphene.String(required=False),
        distinct=graphene.Boolean(default_value=False),
    )

    closed_milestones = graphene.List(
        MilestoneNode,
        limit=graphene.Int(default_value=5),
        login=graphene.String(required=False),
        project=graphene.String(required=False),
        repository=graphene.String(required=False),
        organization=graphene.String(required=False),
        distinct=graphene.Boolean(default_value=False),
    )

    def resolve_open_milestones(
        root,
        info,
        limit,
        login=None,
        organization=None,
        project=None,
        repository=None,
        distinct=False,
    ):
        """Resolve open milestones.

        Args:
            root (object): The root object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): The maximum number of milestones to return.
            login (str, optional): Filter milestones by author login.
            organization (str, optional): Filter milestones by organization login.
            project (str, optional): Filter milestones by project name.
            repository (str, optional): Filter milestones by repository name.
            distinct (bool, optional): Whether to return distinct milestones.

        Returns:
            list: A list of open milestones.

        """
        open_milestones = Milestone.open_milestones.select_related(
            "author",
            "repository",
            "repository__organization",
        ).prefetch_related(
            "issues",
            "pull_requests",
            "labels",
        )

        if login:
            open_milestones = open_milestones.filter(author__login=login)
        if repository:
            open_milestones = open_milestones.filter(repository__name=repository)
        if organization:
            open_milestones = open_milestones.filter(repository__organization__login=organization)
        # if project:
        #     open_milestones = open_milestones.filter(repository__project__name=project)
        if distinct:
            open_milestones = open_milestones.distinct()

        return open_milestones[:limit]

    def resolve_closed_milestones(
        root,
        info,
        limit,
        login=None,
        organization=None,
        project=None,
        repository=None,
        distinct=False,
    ):
        """Resolve closed milestones.

        Args:
            root (object): The root object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): The maximum number of milestones to return.
            login (str, optional): Filter milestones by author login.
            organization (str, optional): Filter milestones by organization login.
            project (str, optional): Filter milestones by project name.
            repository (str, optional): Filter milestones by repository name.
            distinct (bool, optional): Whether to return distinct milestones.

        Returns:
            list: A list of closed milestones.

        """
        closed_milestones = Milestone.closed_milestones.select_related(
            "author",
            "repository",
            "repository__organization",
        ).prefetch_related(
            "issues",
            "pull_requests",
            "labels",
        )

        if login:
            closed_milestones = closed_milestones.filter(author__login=login)
        if repository:
            closed_milestones = closed_milestones.filter(repository__name=repository)
        # if project:
        #     closed_milestones = closed_milestones.filter(repository__project__name=project)

        if organization:
            closed_milestones = closed_milestones.filter(
                repository__organization__login=organization
            )

        if distinct:
            closed_milestones = closed_milestones.distinct()

        return closed_milestones[:limit]
