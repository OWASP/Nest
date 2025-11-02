"""Milestone API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.github.models.generic_issue_model import GenericIssueModel
from apps.github.models.milestone import Milestone as MilestoneModel

router = RouterPaginated(tags=["Milestones"])


class MilestoneBase(Schema):
    """Base schema for Milestone (used in list endpoints)."""

    created_at: datetime
    number: int
    state: GenericIssueModel.State
    title: str
    updated_at: datetime
    url: str


class Milestone(MilestoneBase):
    """Schema for Milestone (minimal fields for list display)."""


class MilestoneDetail(MilestoneBase):
    """Detail schema for Milestone (used in single item endpoints)."""

    body: str
    closed_issues_count: int
    due_on: datetime | None
    open_issues_count: int


class MilestoneError(Schema):
    """Milestone error schema."""

    message: str


class MilestoneFilter(FilterSchema):
    """Filter for Milestone."""

    organization: str | None = Field(
        None,
        description="Organization that milestones belong to (filtered by repository owner)",
        example="OWASP",
    )
    repository: str | None = Field(
        None,
        description="Repository that milestones belong to",
        example="Nest",
    )
    state: GenericIssueModel.State | None = Field(
        None,
        description="Milestone state",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub milestones.",
    operation_id="list_milestones",
    response=list[Milestone],
    summary="List milestones",
)
@decorate_view(cache_response())
def list_milestones(
    request: HttpRequest,
    filters: MilestoneFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Milestone]:
    """Get all milestones."""
    milestones = MilestoneModel.objects.select_related("repository", "repository__organization")

    if filters.organization:
        milestones = milestones.filter(
            repository__organization__login__iexact=filters.organization
        )
    if filters.repository:
        milestones = milestones.filter(repository__name__iexact=filters.repository)
    if filters.state:
        milestones = milestones.filter(state=filters.state)

    if ordering and ordering.lstrip("-") == "updated_at":
        return milestones.order_by(ordering, "id")
    return milestones.order_by(ordering or "-created_at", "-updated_at", "id")


@router.get(
    "/{str:organization_id}/{str:repository_id}/{int:milestone_id}",
    description=(
        "Retrieve a specific GitHub milestone by organization, repository, and milestone number."
    ),
    operation_id="get_milestone",
    response={
        HTTPStatus.NOT_FOUND: MilestoneError,
        HTTPStatus.OK: MilestoneDetail,
    },
    summary="Get milestone",
)
@decorate_view(cache_response())
def get_milestone(
    request: HttpRequest,
    organization_id: str = Path(example="OWASP"),
    repository_id: str = Path(example="Nest"),
    milestone_id: int = Path(example=1),
) -> MilestoneDetail | MilestoneError:
    """Get milestone."""
    try:
        return MilestoneModel.objects.get(
            repository__organization__login__iexact=organization_id,
            repository__name__iexact=repository_id,
            number=milestone_id,
        )
    except MilestoneModel.DoesNotExist:
        return Response({"message": "Milestone not found"}, status=HTTPStatus.NOT_FOUND)
