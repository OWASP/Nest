"""Organization API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import ValidationErrorSchema
from apps.api.rest.v0.structured_search import FieldConfig, apply_structured_search
from apps.github.models.organization import Organization as OrganizationModel

ORGANIZATION_SEARCH_SCHEMA: dict[str, FieldConfig] = {
    "name": {"type": "string", "field": "name", "lookup": "icontains"},
    "location": {"type": "string", "field": "location", "lookup": "icontains"},
}

router = RouterPaginated(tags=["Community"])


class OrganizationBase(Schema):
    """Base schema for Organization (used in list endpoints)."""

    created_at: datetime
    login: str
    name: str
    updated_at: datetime


class Organization(OrganizationBase):
    """Schema for Organization (minimal fields for list display)."""


class OrganizationDetail(OrganizationBase):
    """Detail schema for Organization (used in single item endpoints)."""

    company: str
    location: str


class OrganizationError(Schema):
    """Organization error schema."""

    message: str


class OrganizationFilter(FilterSchema):
    """Filter for Organization."""

    location: str | None = Field(
        None,
        description="Location of the organization",
        example="United States of America",
    )
    q: str | None = Field(None, description="Structured search query")


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub organizations.",
    operation_id="list_organizations",
    response=list[Organization],
    summary="List organizations",
)
@decorate_view(cache_response())
def list_organization(
    request: HttpRequest,
    filters: OrganizationFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Organization]:
    """Get organizations."""
    queryset = apply_structured_search(
        queryset=OrganizationModel.objects.filter(is_owasp_related_organization=True),
        query=filters.q,
        field_schema=ORGANIZATION_SEARCH_SCHEMA,
    )
    return filters.filter(queryset).order_by(ordering or "-created_at")


@router.get(
    "/{str:organization_id}",
    description="Retrieve project details.",
    operation_id="get_organization",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: OrganizationError,
        HTTPStatus.OK: OrganizationDetail,
    },
    summary="Get organization",
)
@decorate_view(cache_response())
def get_organization(
    request: HttpRequest,
    organization_id: str = Path(example="OWASP"),
) -> OrganizationDetail | OrganizationError:
    """Get project."""
    if organization := OrganizationModel.objects.filter(
        is_owasp_related_organization=True,
        login__iexact=organization_id,
    ).first():
        return organization

    return Response({"message": "Organization not found"}, status=HTTPStatus.NOT_FOUND)
