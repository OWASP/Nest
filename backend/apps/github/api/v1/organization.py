"""Organization API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.organization import Organization

router = Router()


class OrganizationSchema(Schema):
    """Schema for Organization."""

    company: str
    created_at: datetime
    location: str
    login: str
    name: str
    updated_at: datetime


@router.get("/", response=list[OrganizationSchema])
@paginate(PageNumberPagination, page_size=100)
def list_organization(request: HttpRequest) -> list[OrganizationSchema]:
    """Get all organizations."""
    organizations = Organization.objects.filter(is_owasp_related_organization=True)
    if not organizations:
        raise HttpError(404, "Organizations not found")
    return organizations
