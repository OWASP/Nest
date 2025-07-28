"""Project API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import Project

router = Router()


class ProjectFilterSchema(FilterSchema):
    """Filter schema for Project."""

    level: ProjectLevel | None = Field(
        None,
        description="Level of the project",
    )


class ProjectSchema(Schema):
    """Schema for Project."""

    created_at: datetime
    description: str
    level: ProjectLevel
    name: str
    updated_at: datetime


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP projects.",
    operation_id="list_projects",
    response={200: list[ProjectSchema]},
    summary="List projects",
    tags=["OWASP"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_projects(
    request: HttpRequest,
    filters: ProjectFilterSchema = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[ProjectSchema]:
    """Get all projects."""
    projects = filters.filter(Project.objects.all())

    if ordering:
        projects = projects.order_by(ordering)

    return projects
