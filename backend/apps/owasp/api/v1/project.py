"""Project API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja.pagination import RouterPaginated

from apps.owasp.models.project import Project

router = RouterPaginated()


class ProjectSchema(Schema):
    """Schema for Project."""

    created_at: datetime
    description: str
    level: str
    name: str
    updated_at: datetime


@router.get("/", response=list[ProjectSchema])
def list_projects(request: HttpRequest) -> list[ProjectSchema] | HttpError:
    """Get all projects."""
    projects = Project.objects.all()
    if not projects:
        raise HttpError(404, "Projects not found")
    return projects
