"""Organization API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

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
def list_organization(request: HttpRequest) -> list[OrganizationSchema]:
    """Get all organizations."""
    return Organization.objects.filter(is_owasp_related_organization=True)
