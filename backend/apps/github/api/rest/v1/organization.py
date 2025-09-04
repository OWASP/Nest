"""Organization API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.organization import Organization

router = Router()


class OrganizationFilterSchema(FilterSchema):
    """Filter schema for Organization."""

    location: str | None = Field(
        None,
        description="Location of the organization",
        example="United States of America",
    )


class OrganizationSchema(Schema):
    """Schema for Organization."""

    company: str
    created_at: datetime
    location: str
    login: str
    name: str
    updated_at: datetime


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub organizations.",
    operation_id="list_organizations",
    response={200: list[OrganizationSchema]},
    summary="List organizations",
    tags=["github"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_organization(
    request: HttpRequest,
    filters: OrganizationFilterSchema = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[OrganizationSchema]:
    """Get all organizations."""
    organizations = filters.filter(Organization.objects.filter(is_owasp_related_organization=True))

    if ordering:
        organizations = organizations.order_by(ordering)

    return organizations
