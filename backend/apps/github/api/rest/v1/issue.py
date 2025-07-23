"""Issue API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.generic_issue_model import GenericIssueModel
from apps.github.models.issue import Issue

router = Router()


class IssueFilterSchema(FilterSchema):
    """Filter schema for Issue."""

    state: GenericIssueModel.State | None = Field(None, description="State of the issue")


class IssueSchema(Schema):
    """Schema for Issue."""

    body: str
    created_at: datetime
    title: str
    state: GenericIssueModel.State
    updated_at: datetime
    url: str


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub issues.",
    operation_id="list_issues",
    response={200: list[IssueSchema]},
    summary="Get all issues",
    tags=["Issues"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_issues(
    request: HttpRequest,
    filters: IssueFilterSchema = Query(..., description="Filter criteria for issues"),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None, description="Ordering field"
    ),
) -> list[IssueSchema]:
    """Get all issues."""
    issues = filters.filter(Issue.objects.all())

    if ordering:
        issues = issues.order_by(ordering)

    return issues
