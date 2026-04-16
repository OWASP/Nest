"""Release API."""

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
from apps.github.models.release import Release as ReleaseModel

router = RouterPaginated(tags=["Releases"])


class ReleaseBase(Schema):
    """Base schema for Release (used in list endpoints)."""

    created_at: datetime
    name: str
    published_at: datetime | None = None
    tag_name: str


class Release(ReleaseBase):
    """Schema for Release (minimal fields for list display)."""


class ReleaseDetail(ReleaseBase):
    """Detail schema for Release (used in single item endpoints)."""

    description: str


class ReleaseError(Schema):
    """Release error schema."""

    message: str


class ReleaseFilter(FilterSchema):
    """Filter for Release."""

    organization: str | None = Field(
        None,
        description="Organization that releases belong to (filtered by repository owner)",
        example="OWASP",
    )
    repository: str | None = Field(
        None,
        description="Repository that releases belong to",
        example="Nest",
    )
    tag_name: str | None = Field(None, description="Tag name of the release", example="0.2.10")


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub releases.",
    operation_id="list_releases",
    summary="List releases",
    response=list[Release],
)
@decorate_view(cache_response())
def list_release(
    request: HttpRequest,
    filters: ReleaseFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "published_at", "-published_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Release]:
    """Get all releases."""
    releases = ReleaseModel.objects.exclude(
        published_at__isnull=True,
    ).select_related(
        "repository",
        "repository__organization",
    )

    if filters.organization:
        releases = releases.filter(repository__organization__login__iexact=filters.organization)

    if filters.repository:
        releases = releases.filter(repository__name__iexact=filters.repository)

    if filters.tag_name:
        releases = releases.filter(tag_name=filters.tag_name)

    primary_order = ordering or "-published_at"
    order_fields = [primary_order]
    if primary_order not in {"created_at", "-created_at"}:
        order_fields.append("-created_at")

    return releases.order_by(*order_fields)


@router.get(
    "/{str:organization_id}/{str:repository_id}/{str:release_id}",
    description="Retrieve a specific GitHub release by organization, repository, and tag name.",
    operation_id="get_release",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: ReleaseError,
        HTTPStatus.OK: ReleaseDetail,
    },
    summary="Get release",
)
@decorate_view(cache_response())
def get_release(
    request: HttpRequest,
    organization_id: str = Path(example="OWASP"),
    repository_id: str = Path(example="Nest"),
    release_id: str = Path(example="0.2.10"),
) -> ReleaseDetail | ReleaseError:
    """Get a specific release by organization, repository, and tag name."""
    try:
        return ReleaseModel.objects.get(
            repository__organization__login__iexact=organization_id,
            repository__name__iexact=repository_id,
            tag_name=release_id,
        )
    except ReleaseModel.DoesNotExist:
        return Response({"message": "Release not found"}, status=HTTPStatus.NOT_FOUND)
