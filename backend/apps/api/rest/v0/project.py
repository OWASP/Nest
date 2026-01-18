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
from apps.api.rest.v0.common import Leader
from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import Project as ProjectModel

router = RouterPaginated(tags=["Projects"])


class ProjectBase(Schema):
    """Base schema for Project (used in list endpoints)."""

    created_at: datetime = Field(
        ...,
        description="Project creation timestamp (ISO 8601).",
        example="2019-09-12T20:15:45Z",
    )
    key: str = Field(
        ...,
        description=(
            "Stable project key used as the identifier in API URLs. "
            "Use this value as `{project_id}` in `GET /api/v0/projects/{project_id}`."
        ),
        example="cheat-sheets",
    )
    level: ProjectLevel = Field(
        ...,
        description="Project maturity level.",
        example="flagship",
    )
    name: str = Field(
        ...,
        description="Human-readable project name.",
        example="OWASP Cheat Sheet Series",
    )
    updated_at: datetime = Field(
        ...,
        description="Last updated timestamp (ISO 8601).",
        example="2025-12-15T15:12:05Z",
    )

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
        description=(
            "Filter by project level.\n\n"
            "Must be one of: `other`, `incubator`, `lab`, `production`, `flagship`."
        ),
        example="flagship",
    )


@router.get(
    "/",
    description=(
        "Retrieve a paginated list of OWASP projects.\n\n"
        "Use this endpoint to discover project keys/IDs that can be used with "
        "`GET /api/v0/projects/{project_id}`.\n\n"
        "### Authentication\n"
        "In non-local environments this endpoint requires an API key in the `X-API-Key` header. "
        "### Pagination\n"
        "Pagination query parameters are provided by the API's configured Django Ninja pagination "
        "class "
        "(see the query params shown below in Swagger).\n\n"
        "Common patterns are either:\n"
        "- `page` and `page_size` (page-number pagination)\n"
        "- `limit` and `offset` (limit-offset pagination)\n\n"
        "### Validation errors\n"
        "Invalid `level`, `ordering`, or pagination values may return `422 Unprocessable Content`."
    ),
    operation_id="list_projects",
    response=list[Project],
    summary="List projects",
    openapi_extra={
        "responses": {
            401: {
                "description": "Unauthorized — missing or invalid API key (non-local environments).",
                "content": {
                    "application/json": {
                        "examples": {
                            "Missing or invalid API key": {
                                "value": {"message": "Missing or invalid API key"}
                            }
                        }
                    }
                },
            },
            404: {
                "description": "Not Found — page out of range (when using page-based pagination).",
                "content": {
                    "application/json": {
                        "examples": {
                            "Page out of range": {
                                "value": {
                                    "detail": "Not Found: Page 3000 not found. Valid pages are 1 to 3."
                                }
                            }
                        }
                    }
                },
            },
            422: {
                "description": "Unprocessable Content — invalid query parameters (e.g., invalid level, ordering, or page).",
                "content": {
                    "application/json": {
                        "examples": {
                            "Invalid level + ordering": {
                                "value": {
                                    "detail": [
                                        {
                                            "type": "enum",
                                            "loc": ["query", "level"],
                                            "msg": "Input should be 'other', 'incubator', 'lab', 'production' or 'flagship'",
                                            "ctx": {"expected": "'other', 'incubator', 'lab', 'production' or 'flagship'"},
                                        },
                                        {
                                            "type": "literal_error",
                                            "loc": ["query", "ordering"],
                                            "msg": "Input should be 'created_at', '-created_at', 'updated_at' or '-updated_at'",
                                            "ctx": {"expected": "'created_at', '-created_at', 'updated_at' or '-updated_at'"},
                                        },
                                    ]
                                }
                            },
                            "Invalid page (page=0)": {
                                "value": {
                                    "detail": [
                                        {
                                            "type": "greater_than_equal",
                                            "loc": ["query", "page"],
                                            "msg": "Input should be greater than or equal to 1",
                                            "ctx": {"ge": 1},
                                        }
                                    ]
                                }
                            },
                        }
                    }
                },
            },
        }
    },
)
@decorate_view(cache_response())
def list_projects(
    request: HttpRequest,
    filters: ProjectFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description=(
            "Sort order for results.\n\n"
            "Allowed values: `created_at`, `-created_at`, `updated_at`, `-updated_at`.\n"
            "If not provided, the API applies a default ordering."
        ),
        example="-updated_at",
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

    return Response({"message": "Project not found"}, status=HTTPStatus.NOT_FOUND)
