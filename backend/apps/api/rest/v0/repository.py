"""Repository API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import ValidationErrorSchema
from apps.api.rest.v0.structured_search import FieldConfig, apply_structured_search
from apps.github.models.repository import Repository as RepositoryModel

REPOSITORY_SEARCH_SCHEMA: dict[str, FieldConfig] = {
    "name": {"type": "string", "field": "name", "lookup": "icontains"},
    "stars": {"type": "number", "field": "stars_count"},
    "forks": {"type": "number", "field": "forks_count"},
}

router = RouterPaginated(tags=["Repositories"])


class RepositoryBase(Schema):
    """Base schema for Repository (used in list endpoints)."""

    created_at: datetime
    name: str
    updated_at: datetime


class Repository(RepositoryBase):
    """Schema for Repository (minimal fields for list display)."""


class RepositoryDetail(RepositoryBase):
    """Detail schema for Repository (used in single item endpoints)."""

    commits_count: int
    contributors_count: int
    description: str | None = None
    forks_count: int
    open_issues_count: int
    stars_count: int


class RepositoryError(Schema):
    """Repository error schema."""

    message: str


class RepositoryFilter(FilterSchema):
    """Filter for Repository."""

    organization_id: str | None = Field(
        None,
        description="Organization that repositories belong to",
        example="OWASP",
    )
    q: str | None = Field(
        None,
        description="Structured search query",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub repositories.",
    operation_id="list_repositories",
    summary="List repositories",
    response=list[Repository],
)
@decorate_view(cache_response())
def list_repository(
    request: HttpRequest,
    filters: RepositoryFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Repository]:
    """Get all repositories."""
    repositories = RepositoryModel.objects.select_related("organization")

    if filters.organization_id:
        repositories = repositories.filter(organization__login__iexact=filters.organization_id)

    repositories = apply_structured_search(repositories, filters.q, REPOSITORY_SEARCH_SCHEMA)
    return repositories.order_by(ordering or "-created_at", "-updated_at")


@router.get(
    "/{str:organization_id}/{str:repository_id}",
    description="Retrieve a specific GitHub repository by organization and repository name.",
    operation_id="get_repository",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: RepositoryError,
        HTTPStatus.OK: RepositoryDetail,
    },
    summary="Get repository",
)
@decorate_view(cache_response())
def get_repository(
    request: HttpRequest,
    organization_id: str = Path(example="OWASP"),
    repository_id: str = Path(example="Nest"),
) -> RepositoryDetail | RepositoryError:
    """Get a specific repository by organization and repository name."""
    try:
        return RepositoryModel.objects.select_related("organization").get(
            organization__login__iexact=organization_id,
            name__iexact=repository_id,
        )
    except RepositoryModel.DoesNotExist:
        return Response({"message": "Repository not found"}, status=HTTPStatus.NOT_FOUND)
