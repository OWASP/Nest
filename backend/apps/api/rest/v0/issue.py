"""Issue API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import ValidationErrorSchema
from apps.github.models.generic_issue_model import GenericIssueModel
from apps.github.models.issue import Issue as IssueModel

router = RouterPaginated(tags=["Issues"])


class IssueBase(Schema):
    """Base schema for Issue (used in list endpoints)."""

    created_at: datetime
    state: GenericIssueModel.State
    title: str
    updated_at: datetime
    url: str


class Issue(IssueBase):
    """Schema for Issue (minimal fields for list display)."""


class IssueDetail(IssueBase):
    """Detail schema for Issue (used in single item endpoints)."""

    body: str


class IssueError(Schema):
    """Issue error schema."""

    message: str


class IssueFilter(FilterSchema):
    """Filter for Issue."""

    organization: str | None = Field(
        None,
        description="Organization that issues belong to (filtered by repository owner)",
        example="OWASP",
    )
    repository: str | None = Field(
        None,
        description="Repository that issues belong to",
        example="Nest",
    )
    state: GenericIssueModel.State | None = Field(
        None,
        description="Issue state",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub issues.",
    operation_id="list_issues",
    response=list[Issue],
    summary="List issues",
)
@decorate_view(cache_response())
def list_issues(
    request: HttpRequest,
    filters: IssueFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Issue]:
    """Get all issues."""
    issues = IssueModel.objects.select_related("repository", "repository__organization")

    if filters.organization:
        issues = issues.filter(repository__organization__login__iexact=filters.organization)

    if filters.repository:
        issues = issues.filter(repository__name__iexact=filters.repository)
    if filters.state:
        issues = issues.filter(state=filters.state)

    primary_order = ordering or "-created_at"
    order_fields = [primary_order]
    if primary_order not in {"updated_at", "-updated_at"}:
        order_fields.append("-updated_at")

    return issues.order_by(*order_fields)


@router.get(
    "/{str:organization_id}/{str:repository_id}/{int:issue_id}",
    description="Retrieve a specific GitHub issue by organization, repository, and issue number.",
    operation_id="get_issue",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: IssueError,
        HTTPStatus.OK: IssueDetail,
    },
    summary="Get issue",
)
@decorate_view(cache_response())
def get_issue(
    request: HttpRequest,
    organization_id: str = Path(example="OWASP"),
    repository_id: str = Path(example="Nest"),
    issue_id: int = Path(example=1234),
) -> IssueDetail | IssueError:
    """Get a specific issue by organization, repository, and issue number."""
    try:
        return IssueModel.objects.get(
            repository__organization__login__iexact=organization_id,
            repository__name__iexact=repository_id,
            number=issue_id,
        )
    except IssueModel.DoesNotExist:
        return Response({"message": "Issue not found"}, status=HTTPStatus.NOT_FOUND)
