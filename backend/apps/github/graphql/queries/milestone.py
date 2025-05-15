"""Github Milestone Queries."""

import graphene
from django.core.exceptions import ValidationError

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
        state=graphene.String(default_value="open"),
    )

    def resolve_milestones(
        root,
        info,
        limit,
        login=None,
        organization=None,
        repository=None,
        state="open",
    ):
        """Resolve milestones.

        Args:
            root (object): The root object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): The maximum number of milestones to return.
            login (str, optional): Filter milestones by author login.
            organization (str, optional): Filter milestones by organization login.
            repository (str, optional): Filter milestones by repository name.
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

        if login:
            milestones = milestones.filter(author__login=login)
        if repository:
            milestones = milestones.filter(repository__name=repository)
        if organization:
            milestones = milestones.filter(repository__organization__login=organization)

        return milestones[:limit]
