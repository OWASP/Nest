"""Organization API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.organization import Organization

router = Router()


class OrganizationFilterSchema(FilterSchema):
    """Filter schema for Organization."""

    company: str | None = None
    location: str | None = None


class OrganizationSchema(Schema):
    """Schema for Organization."""

    company: str
    created_at: datetime
    location: str
    login: str
    name: str
    updated_at: datetime


VALID_ORGANIZATION_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get(
    "/",
    summary="Get all organizations",
    tags=["Organizations"],
    response={200: list[OrganizationSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_organization(
    request: HttpRequest,
    filters: OrganizationFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[OrganizationSchema]:
    """
    Retrieves a paginated list of organizations, optionally filtered by company and location, and ordered by creation or update time.
    
    Parameters:
        filters (OrganizationFilterSchema): Optional filters for company and location.
        ordering (str, optional): Field to order results by; must be "created_at" or "updated_at" if provided.
    
    Returns:
        list[OrganizationSchema]: A paginated list of organizations matching the filters and ordering.
    """
    organizations = filters.filter(Organization.objects.filter(is_owasp_related_organization=True))
    if ordering and ordering in VALID_ORGANIZATION_ORDERING_FIELDS:
        organizations = organizations.order_by(ordering)
    return organizations
