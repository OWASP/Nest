"""Github Milestone Queries."""

import graphene
from django.db.models import OuterRef, Subquery

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
        repository=graphene.String(required=False),
        distinct=graphene.Boolean(default_value=False),
    )

    closed_milestones = graphene.List(
        MilestoneNode,
        limit=graphene.Int(default_value=5),
        login=graphene.String(required=False),
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

        if distinct:
            latest_milestone_per_author = (
                open_milestones.filter(author_id=OuterRef("author_id"))
                .order_by("-created_at")
                .values("id")[:1]
            )
            open_milestones = open_milestones.filter(
                id__in=Subquery(latest_milestone_per_author),
            ).order_by("-created_at")

        return open_milestones[:limit]

    def resolve_closed_milestones(
        root,
        info,
        limit,
        login=None,
        organization=None,
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

        if organization:
            closed_milestones = closed_milestones.filter(
                repository__organization__login=organization
            )

        if distinct:
            latest_milestone_per_author = (
                closed_milestones.filter(author_id=OuterRef("author_id"))
                .order_by("-created_at")
                .values("id")[:1]
            )
            closed_milestones = closed_milestones.filter(
                id__in=Subquery(latest_milestone_per_author),
            ).order_by("-created_at")

        return closed_milestones[:limit]
