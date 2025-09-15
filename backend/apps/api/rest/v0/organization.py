"""Organization API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Path, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate
from ninja.responses import Response

from apps.github.models.organization import Organization

router = Router()


class OrganizationErrorResponse(Schema):
    """Organization error response schema."""

    message: str


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
    tags=["Community"],
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
    """Get organizations."""
    return filters.filter(
        Organization.objects.filter(
            is_owasp_related_organization=True,
        ).order_by(ordering or "-created_at")
    )


@router.get(
    "/{str:organization_id}",
    description="Retrieve project details.",
    operation_id="get_organization",
    response={
        HTTPStatus.NOT_FOUND: OrganizationErrorResponse,
        HTTPStatus.OK: OrganizationSchema,
    },
    summary="Get organization",
    tags=["Community"],
)
def get_organization(
    request: HttpRequest,
    organization_id: str = Path(example="OWASP"),
) -> OrganizationSchema | OrganizationErrorResponse:
    """Get project."""
    if organization := Organization.objects.filter(
        is_owasp_related_organization=True,
        login__iexact=organization_id,
    ).first():
        return organization

    return Response({"message": "Organization not found"}, status=HTTPStatus.NOT_FOUND)
