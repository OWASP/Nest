"""Project API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import Project as ProjectModel

router = RouterPaginated(tags=["Projects"])


class ProjectBase(Schema):
    """Base schema for Project (used in list endpoints)."""

    created_at: datetime
    key: str
    level: ProjectLevel
    name: str
    updated_at: datetime

    @staticmethod
    def resolve_key(obj):
        """Resolve key."""
        return obj.nest_key


class Project(ProjectBase):
    """Schema for Project (minimal fields for list display)."""


class ProjectDetail(ProjectBase):
    """Detail schema for Project (used in single item endpoints)."""

    description: str


class ProjectError(Schema):
    """Project error schema."""

    message: str


class ProjectFilter(FilterSchema):
    """Filter for Project."""

    level: ProjectLevel | None = Field(
        None,
        description="Level of the project",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP projects.",
    operation_id="list_projects",
    response=list[Project],
    summary="List projects",
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
def list_projects(
    request: HttpRequest,
    filters: ProjectFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
        example="-created_at",
    ),
) -> list[Project]:
    """Get projects."""
    return filters.filter(ProjectModel.active_projects.order_by(ordering or "-created_at"))


@router.get(
    "/{str:project_id}",
    description="Retrieve project details.",
    operation_id="get_project",
    response={
        HTTPStatus.NOT_FOUND: ProjectError,
        HTTPStatus.OK: ProjectDetail,
    },
    summary="Get project",
)
def get_project(
    request: HttpRequest,
    project_id: str = Path(example="Nest"),
) -> ProjectDetail | ProjectError:
    """Get project."""
    if project := ProjectModel.active_projects.filter(
        key__iexact=(
            project_id if project_id.startswith("www-project-") else f"www-project-{project_id}"
        )
    ).first():
        return project

    return Response({"message": "Project not found"}, status=HTTPStatus.NOT_FOUND)
