"""Project API."""
from .errors import project_not_found
from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
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
    def resolve_key(obj: ProjectModel) -> str:
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
@decorate_view(cache_response())
def list_projects(
    request: HttpRequest,
    filters: ProjectFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Project]:
    """Get projects."""
    return filters.filter(
        ProjectModel.active_projects.order_by(
            ordering or "-level_raw", "-stars_count", "-forks_count"
        )
    )


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
@decorate_view(cache_response())
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

    return project_not_found()
