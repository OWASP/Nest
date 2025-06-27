"""Project API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

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
@paginate(PageNumberPagination, page_size=100)
def list_projects(request: HttpRequest) -> list[ProjectSchema]:
    """Get all projects."""
    projects = Project.objects.all()
    if not projects:
        raise HttpError(404, "Projects not found")
    return projects
