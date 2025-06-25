"""Issue API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

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


@router.get("/", response=list[IssueSchema])
def list_issues(request: HttpRequest) -> list[IssueSchema]:
    """Get all issues."""
    return Issue.objects.all()
