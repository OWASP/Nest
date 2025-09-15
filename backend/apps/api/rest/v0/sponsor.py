"""Sponsor API."""

from http import HTTPStatus
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Path, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate
from ninja.responses import Response

from apps.owasp.models.sponsor import Sponsor

router = Router()


class SponsorErrorResponse(Schema):
    """Sponsor error response schema."""

    message: str


class SponsorFilterSchema(FilterSchema):
    """Filter schema for Sponsor."""

    sponsor_type: Sponsor.SponsorType | None = Field(
        None,
        description="Type of sponsor",
    )
    is_member: bool | None = Field(
        None,
        description="Member status of the sponsor",
    )
    member_type: Sponsor.MemberType | None = Field(
        None,
        description="Member type of the sponsor",
    )


class SponsorSchema(Schema):
    """Schema for Sponsor."""

    key: str
    name: str
    description: str
    url: str
    job_url: str
    image_url: str
    sponsor_type: str
    member_type: str
    is_member: bool


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP sponsors.",
    operation_id="list_sponsors",
    response={HTTPStatus.OK: list[SponsorSchema]},
    summary="List sponsors",
    tags=["Sponsors"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_sponsors(
    request: HttpRequest,
    filters: SponsorFilterSchema = Query(...),
    ordering: Literal["name", "-name"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[SponsorSchema]:
    """Get all sponsors."""
    return filters.filter(Sponsor.objects.all()).order_by(ordering or "name")


@router.get(
    "/{str:sponsor_key}",
    description="Retrieve a sponsor details.",
    operation_id="get_sponsor",
    response={
        HTTPStatus.NOT_FOUND: SponsorErrorResponse,
        HTTPStatus.OK: SponsorSchema,
    },
    summary="Get sponsor",
    tags=["Sponsors"],
)
def get_sponsor(
    request: HttpRequest,
    sponsor_key: str = Path(..., example="adobe"),
) -> SponsorSchema | SponsorErrorResponse:
    """Get sponsor."""
    sponsor = Sponsor.objects.filter(key=sponsor_key).first()

    if not sponsor:
        return Response(
            {"message": "Sponsor not found"},
            status=HTTPStatus.NOT_FOUND,
        )

    return sponsor
