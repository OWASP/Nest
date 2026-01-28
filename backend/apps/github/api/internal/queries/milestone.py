"""Github Milestone Queries."""

import enum

import strawberry
import strawberry_django
from django.db.models import OuterRef, Subquery

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.models.generic_issue_model import GenericIssueModel
from apps.github.models.milestone import Milestone

MAX_LIMIT = 1000


@strawberry.enum
class MilestoneStateEnum(str, enum.Enum):
    """Milestone state filter options."""

    CLOSED = GenericIssueModel.State.CLOSED.value
    OPEN = GenericIssueModel.State.OPEN.value


@strawberry.type
class MilestoneQuery:
    """Github Milestone Queries."""

    @strawberry_django.field
    def recent_milestones(
        self,
        *,
        distinct: bool = False,
        limit: int = 5,
        login: str | None = None,
        organization: str | None = None,
        state: MilestoneStateEnum | None = None,
    ) -> list[MilestoneNode]:
        """Resolve milestones.

        Args:
            distinct (bool): Whether to return distinct milestones.
            limit (int): The maximum number of milestones to return.
            login (str, optional): The GitHub username to filter milestones.
            organization (str, optional): The GitHub organization to filter milestones.
            state (MilestoneStateEnum, optional): The state filter. Returns all if not provided.

        Returns:
            list[MilestoneNode]: A list of milestones.

        """
        match state:
            case MilestoneStateEnum.OPEN:
                milestones = Milestone.open_milestones.all()
            case MilestoneStateEnum.CLOSED:
                milestones = Milestone.closed_milestones.all()
            case _:
                milestones = Milestone.objects.all()

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

        validated_limit = normalize_limit(limit, MAX_LIMIT)
        if validated_limit is None:
            return []

        return milestones.order_by("-created_at")[:validated_limit]
