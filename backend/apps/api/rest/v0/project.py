"""Project API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.errors import ValidationError
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import Leader, ValidationErrorSchema
from apps.api.rest.v0.structured_search import FieldConfig, apply_structured_search
from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import Project as ProjectModel

PROJECT_SEARCH_FIELDS: dict[str, FieldConfig] = {
    "name": {
        "type": "string",
        "lookup": "icontains",
    },
    "stars": {
        "type": "number",
        "field": "stars_count",
    },
}

VALID_PROJECT_LEVELS = frozenset(ProjectLevel.values)


def parse_type_filter(type_param: str | None) -> list[ProjectLevel] | None:
    """Parse and validate the type query parameter.

    Args:
        type_param: Comma-separated string of project levels.

    Returns:
        List of valid ProjectLevel values, or None if type_param is empty/None.

    Raises:
        ValidationError: If any value is invalid.

    """
    if not type_param or not type_param.strip():
        return None

    values = [v.strip().lower() for v in type_param.split(",") if v.strip()]
    if not values:
        return None

    invalid = [v for v in values if v not in VALID_PROJECT_LEVELS]
    if invalid:
        raise ValidationError(
            [
                {
                    "loc": ["query", "type"],
                    "msg": f"Invalid project level(s): {invalid}. "
                    f"Valid values: {', '.join(sorted(VALID_PROJECT_LEVELS))}",
                    "type": "value_error",
                }
            ]
        )

    return [ProjectLevel(v) for v in values]


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
        description="Structured search query (e.g. 'name:security stars:>100')",
    )
    type: str | None = Field(
        None,
        description="Filter by project level (comma-separated for multiple). "
        "Valid values: flagship, production, lab, incubator, other",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP projects.",
    operation_id="list_projects",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.OK: list[Project],
    },
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
    queryset = apply_structured_search(
        queryset=ProjectModel.active_projects,
        query=filters.q,
        field_schema=PROJECT_SEARCH_FIELDS,
    )

    if filters.level is not None:
        queryset = queryset.filter(level=filters.level)

    type_levels = parse_type_filter(filters.type)
    if type_levels is not None:
        queryset = queryset.filter(level__in=type_levels)

    return queryset.order_by(ordering or "-level_raw", "-stars_count", "-forks_count")


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
