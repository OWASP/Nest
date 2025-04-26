"""Github Milestone Queries."""

import graphene
from django.db.models import OuterRef, Subquery

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.milestone import MilestoneNode
from apps.github.models.milestone import Milestone


class MilestoneQuery(BaseQuery):
    """Github Milestone Queries."""

    milestones = graphene.List(
        MilestoneNode,
        limit=graphene.Int(default_value=5),
        login=graphene.String(required=False),
        organization=graphene.String(required=False),
        repository=graphene.String(required=False),
        distinct=graphene.Boolean(default_value=False),
        close=graphene.Boolean(default_value=True),
    )

    def resolve_milestones(
        root,
        info,
        limit,
        login=None,
        organization=None,
        repository=None,
        distinct=False,
        close=True,
    ):
        """Resolve milestones.

        Args:
            root (object): The root object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): The maximum number of milestones to return.
            login (str, optional): Filter milestones by author login.
            organization (str, optional): Filter milestones by organization login.
            repository (str, optional): Filter milestones by repository name.
            distinct (bool, optional): Whether to return distinct milestones.
            close (bool, optional): Whether to return open or closed milestones.

        Returns:
            list: A list of milestones.

        """
        milestones = Milestone.closed_milestones if close else Milestone.open_milestones
        milestones = milestones.select_related(
            "author",
            "repository",
            "repository__organization",
        ).prefetch_related(
            "issues",
            "pull_requests",
            "labels",
        )

        if login:
            milestones = milestones.filter(author__login=login)
        if repository:
            milestones = milestones.filter(repository__name=repository)
        if organization:
            milestones = milestones.filter(repository__organization__login=organization)

        if distinct:
            latest_milestone_per_author = (
                milestones.filter(author_id=OuterRef("author_id"))
                .order_by("-created_at")
                .values("id")[:1]
            )
            milestones = milestones.filter(
                id__in=Subquery(latest_milestone_per_author),
            ).order_by("-created_at")

        return milestones[:limit]
