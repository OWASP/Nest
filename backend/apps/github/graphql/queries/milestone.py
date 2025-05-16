"""Github Milestone Queries."""

import graphene
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Subquery

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.milestone import MilestoneNode
from apps.github.models.milestone import Milestone


class MilestoneQuery(BaseQuery):
    """Github Milestone Queries."""

    milestones = graphene.List(
        MilestoneNode,
        distinct=graphene.Boolean(default_value=False),
        limit=graphene.Int(default_value=5),
        state=graphene.String(default_value="open"),
    )

    def resolve_milestones(
        root,
        info,
        *,
        distinct: bool=False,
        limit: int=5,
        state: str="open",
    ):
        """Resolve milestones.

        Args:
            root (object): The root object.
            info (ResolveInfo): The GraphQL execution context.
            distinct (bool): Whether to return distinct milestones.
            limit (int): The maximum number of milestones to return.
            state (str, optional): The state of the milestones to return.

        Returns:
            list: A list of milestones.

        """
        match state.lower():
            case "open":
                milestones = Milestone.open_milestones.all()
            case "closed":
                milestones = Milestone.closed_milestones.all()
            case "all":
                milestones = Milestone.objects.all()
            case _:
                message = f"Invalid state: {state}. Valid states are 'open', 'closed', or 'all'."
                raise ValidationError(message)

        milestones = milestones.select_related(
            "author",
            "repository",
            "repository__organization",
        ).prefetch_related(
            "issues",
            "labels",
            "pull_requests",
        )

        if distinct:
            latest_milestone_per_author = (
                milestones.filter(author_id=OuterRef("author_id"))
                .order_by("-created_at")
                .values("id")[:1]
            )
            milestones = milestones.filter(
                id__in=Subquery(latest_milestone_per_author),
            ).order_by(
                "-created_at",
            )

        return milestones[:limit]
