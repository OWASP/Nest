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


@router.get("/", response={200: list[OrganizationSchema]})
@decorate_view(cache_page(settings.API_CACHE_TIME))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_organization(
    request: HttpRequest,
    filters: OrganizationFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[OrganizationSchema]:
    """Get all organizations."""
    organizations = filters.filter(Organization.objects.filter(is_owasp_related_organization=True))
    if ordering and ordering in VALID_ORGANIZATION_ORDERING_FIELDS:
        organizations = organizations.order_by(ordering)
    return organizations
