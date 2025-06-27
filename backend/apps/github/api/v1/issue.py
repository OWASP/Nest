"""Issue API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.issue import Issue

router = Router()


class IssueSchema(Schema):
    """Schema for Issue."""

    body: str
    created_at: datetime
    title: str
    state: str
    updated_at: datetime
    url: str


@router.get("/", response={200: list[IssueSchema], 404: dict})
@paginate(PageNumberPagination, page_size=100)
def list_issues(request: HttpRequest) -> list[IssueSchema] | dict:
    """Get all issues."""
    issues = Issue.objects.all()
    if not issues.exists():
        raise HttpError(404, "Issues not found")
    return issues
