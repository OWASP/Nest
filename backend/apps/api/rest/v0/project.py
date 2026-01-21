"""Project API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import Leader, ValidationErrorSchema
from apps.common.utils import apply_structured_search
from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import Project as ProjectModel

PROJECT_SEARCH_FIELDS = {
    "name": "string",
    "is_active": "boolean",
    "stars_count": "number",
}

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
    leaders: list[Leader]

    @staticmethod
    def resolve_leaders(obj):
        """Resolve leaders."""
        return [
            Leader(key=leader.member.login if leader.member else None, name=leader.member_name)
            for leader in obj.entity_leaders
        ]


class ProjectError(Schema):
    """Project error schema."""

    message: str


class ProjectFilter(FilterSchema):
    """Filter for Project."""

    level: ProjectLevel | None = Field(
        None,
        description="Level of the project",
    )
    q: str | None = Field(
        None,
        description="Structured search query (e.g. 'name:nest stars_count>100')",
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
    queryset = ProjectModel.active_projects.order_by(
        ordering or "-level_raw", "-stars_count", "-forks_count"
    )

    queryset = apply_structured_search(
        queryset=queryset,
        query=filters.q,
        field_schema=PROJECT_SEARCH_FIELDS,
    )

    if filters.level is not None:
        queryset = queryset.filter(level=filters.level)

    return queryset


@router.get(
    "/{str:project_id}",
    description="Retrieve project details.",
    operation_id="get_project",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
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

    return Response({"message": "Project not found"}, status=HTTPStatus.NOT_FOUND)
