"""Project API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Path, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate
from ninja.responses import Response

from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import Project

router = Router()


class ProjectErrorResponse(Schema):
    """Project error response schema."""

    message: str


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
    tags=["Projects"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_projects(
    request: HttpRequest,
    filters: ProjectFilterSchema = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
        example="-created_at",
    ),
) -> list[ProjectSchema]:
    """Get projects."""
    return filters.filter(Project.active_projects.order_by(ordering or "-created_at"))


@router.get(
    "/{str:project_id}",
    description="Retrieve project details.",
    operation_id="get_project",
    response={
        HTTPStatus.NOT_FOUND: ProjectErrorResponse,
        HTTPStatus.OK: ProjectSchema,
    },
    summary="Get project",
    tags=["Projects"],
)
def get_project(
    request: HttpRequest,
    project_id: str = Path(example="Nest"),
) -> ProjectSchema | ProjectErrorResponse:
    """Get project."""
    if project := Project.active_projects.filter(
        key__iexact=(
            project_id if project_id.startswith("www-project-") else f"www-project-{project_id}"
        )
    ).first():
        return project

    return Response({"message": "Project not found"}, status=HTTPStatus.NOT_FOUND)
