"""Issue API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from apps.github.models.issue import Issue

router = Router()


class IssueSchema(BaseModel):
    """Schema for Issue."""

    model_config = {"from_attributes": True}

    body: str
    created_at: datetime
    title: str
    state: str
    updated_at: datetime
    url: str


@router.get("/", response=list[IssueSchema])
def get_issue(request: HttpRequest) -> list[IssueSchema]:
    """Get all issues."""
    return Issue.objects.all()
