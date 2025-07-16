"""Organization API."""

from datetime import datetime

from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import CACHE_TIME, PAGE_SIZE
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


@router.get("/", response={200: list[OrganizationSchema], 404: dict})
@decorate_view(cache_page(CACHE_TIME))
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_organization(
    request: HttpRequest, filters: OrganizationFilterSchema = Query(...)
) -> list[OrganizationSchema] | dict:
    """Get all organizations."""
    organizations = filters.filter(Organization.objects.filter(is_owasp_related_organization=True))
    if not organizations.exists():
        raise HttpError(404, "Organizations not found")
    return organizations
