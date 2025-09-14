"""Sponsor API."""

from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.sponsor import Sponsor

router = Router()


class SponsorFilterSchema(FilterSchema):
    """Filter schema for Sponsor."""

    sponsor_type: str | None = Field(
        None,
        description="Filter by the type of sponsorship (e.g., Gold, Silver, Platinum).",
        example="Silver",
    )

    is_member: bool | None = Field(
        None,
        description="Filter by corporate sponsor status.",
        example=True,
    )

    member_type: str | None = Field(
        None,
        description="Filter by the corporate membership type (e.g., Gold, Silver, Platinum).",
        example="Silver",
    )


class SponsorSchema(Schema):
    """Schema for Sponsor."""

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
    summary="List sponsors",
    tags=["Sponsors"],
    response={200: list[SponsorSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_sponsors(
    request: HttpRequest,
    filters: SponsorFilterSchema = Query(...),
    ordering: Literal["name", "-name", "created_at", "-created_at"] | None = Query(
        None,
        description="Ordering field. Use '-' for descending order.",
    ),
) -> list[Sponsor]:
    """Get all sponsors."""
    sponsors = filters.filter(Sponsor.objects.all())

    if ordering:
        sponsors = sponsors.order_by(ordering)

    return sponsors
