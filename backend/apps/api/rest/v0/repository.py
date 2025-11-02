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
from apps.github.models.repository import Repository as RepositoryModel

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

    description: str | None = None


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

    if ordering:
        return repositories.order_by(ordering, "id")
    return repositories.order_by("-created_at", "-updated_at", "id")


@router.get(
    "/{str:organization_id}/{str:repository_id}",
    description="Retrieve a specific GitHub repository by organization and repository name.",
    operation_id="get_repository",
    response={
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
