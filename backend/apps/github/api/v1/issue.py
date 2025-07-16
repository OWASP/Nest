"""Issue API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import PAGE_SIZE
from apps.github.models.issue import Issue

router = Router()


class IssueFilterSchema(FilterSchema):
    """Filter schema for Issue."""

    state: str | None = None


class IssueSchema(Schema):
    """Schema for Issue."""

    body: str
    created_at: datetime
    title: str
    state: str
    updated_at: datetime
    url: str


@router.get("/", response={200: list[IssueSchema], 404: dict})
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_issues(
    request: HttpRequest, filters: IssueFilterSchema = Query(...)
) -> list[IssueSchema] | dict:
    """Get all issues."""
    issues = filters.filter(Issue.objects.all())

    if not issues.exists():
        raise HttpError(404, "Issues not found")
    return issues
