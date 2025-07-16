"""Project API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import PAGE_SIZE
from apps.owasp.models.project import Project

router = Router()


class ProjectFilterSchema(FilterSchema):
    """Filter schema for Project."""

    level: str | None = None


class ProjectSchema(Schema):
    """Schema for Project."""

    created_at: datetime
    description: str
    level: str
    name: str
    updated_at: datetime


@router.get("/", response={200: list[ProjectSchema], 404: dict})
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_projects(
    request: HttpRequest, filters: ProjectFilterSchema = Query(...)
) -> list[ProjectSchema] | dict:
    """Get all projects."""
    projects = filters.filter(Project.objects.all())
    if not projects.exists():
        raise HttpError(404, "Projects not found")
    return projects
