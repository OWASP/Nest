"""Github Milestone Queries."""

import strawberry
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Subquery

from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.models.milestone import Milestone


@strawberry.type
class MilestoneQuery:
    """Github Milestone Queries."""

    @strawberry.field
    def recent_milestones(
        self,
        *,
        distinct: bool = False,
        limit: int = 5,
        login: str | None = None,
        organization: str | None = None,
        state: str = "open",
    ) -> list[MilestoneNode]:
        """Resolve milestones.

        Args:
            distinct (bool): Whether to return distinct milestones.
            limit (int): The maximum number of milestones to return.
            login (str, optional): The GitHub username to filter milestones.
            organization (str, optional): The GitHub organization to filter milestones.
            state (str, optional): The state of the milestones to return.

        Returns:
            list[MilestoneNode]: A list of milestones.

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
            milestones = milestones.filter(
                author__login=login,
            )

        if organization:
            milestones = milestones.filter(
                repository__organization__login=organization,
            )

        if distinct:
            latest_milestone_per_author = (
                milestones.filter(author_id=OuterRef("author_id"))
                .order_by("-created_at")
                .values("id")[:1]
            )
            milestones = milestones.filter(
                id__in=Subquery(latest_milestone_per_author),
            )

        return milestones.order_by(
            "-created_at",
        )[:limit]
