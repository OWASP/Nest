"""Project API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

from apps.owasp.models.project import Project

router = Router()


class ProjectSchema(Schema):
    """Schema for Project."""

    created_at: datetime
    description: str
    level: str
    name: str
    updated_at: datetime


@router.get("/", response=list[ProjectSchema])
def list_projects(request: HttpRequest) -> list[ProjectSchema]:
    """Get all projects."""
    return Project.objects.all()
