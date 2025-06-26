"""Issue API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja.pagination import RouterPaginated

from apps.github.models.issue import Issue

router = RouterPaginated()


class IssueSchema(Schema):
    """Schema for Issue."""

    body: str
    created_at: datetime
    title: str
    state: str
    updated_at: datetime
    url: str


@router.get("/", response=list[IssueSchema])
def list_issues(request: HttpRequest) -> list[IssueSchema] | HttpError:
    """Get all issues."""
    issues = Issue.objects.all()
    if not issues:
        raise HttpError(404, "Issues not found")
    return issues
