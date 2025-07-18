"""Issue API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

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


VALID_ISSUE_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get("/", response={200: list[IssueSchema]})
@decorate_view(cache_page(settings.API_CACHE_TIME))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_issues(
    request: HttpRequest,
    filters: IssueFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[IssueSchema]:
    """Get all issues."""
    issues = filters.filter(Issue.objects.all())

    if ordering and ordering in VALID_ISSUE_ORDERING_FIELDS:
        issues = issues.order_by(ordering)

    return issues
