"""Sponsor API."""

from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import ValidationErrorSchema
from apps.owasp.models.sponsor import Sponsor as SponsorModel

router = RouterPaginated(tags=["Sponsors"])


class SponsorBase(Schema):
    """Base schema for Sponsor (used in list endpoints)."""

    image_url: str
    key: str
    name: str
    sponsor_type: str
    url: str


class Sponsor(SponsorBase):
    """Schema for Sponsor (minimal fields for list display)."""


class SponsorDetail(SponsorBase):
    """Detail schema for Sponsor (used in single item endpoints)."""

    description: str
    is_member: bool
    job_url: str
    member_type: str


class SponsorError(Schema):
    """Sponsor error schema."""

    message: str


class SponsorFilter(FilterSchema):
    """Filter for Sponsor."""

    is_member: bool | None = Field(
        None,
        description="Member status of the sponsor",
    )
    member_type: SponsorModel.MemberType | None = Field(
        None,
        description="Member type of the sponsor",
    )

    sponsor_type: str | None = Field(
        None,
        description="Filter by the type of sponsorship (e.g., Gold, Silver, Platinum).",
        example="Silver",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP sponsors.",
    operation_id="list_sponsors",
    response=list[Sponsor],
    summary="List sponsors",
)
@decorate_view(cache_response())
def list_sponsors(
    request: HttpRequest,
    filters: SponsorFilter = Query(...),
    ordering: Literal["name", "-name"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Sponsor]:
    """Get sponsors."""
    return filters.filter(SponsorModel.objects.order_by(ordering or "name"))


@router.get(
    "/{str:sponsor_id}",
    description="Retrieve a sponsor details.",
    operation_id="get_sponsor",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: SponsorError,
        HTTPStatus.OK: SponsorDetail,
    },
    summary="Get sponsor",
)
@decorate_view(cache_response())
def get_sponsor(
    request: HttpRequest,
    sponsor_id: str = Path(..., example="adobe"),
) -> SponsorDetail | SponsorError:
    """Get sponsor."""
    if sponsor := SponsorModel.objects.filter(key__iexact=sponsor_id).first():
        return sponsor

    return Response({"message": "Sponsor not found"}, status=HTTPStatus.NOT_FOUND)
