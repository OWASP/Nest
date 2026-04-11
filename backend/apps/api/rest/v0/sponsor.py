"""Sponsor API."""

from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import ValidationErrorSchema
from apps.common.utils import slugify
from apps.owasp.models.sponsor import Sponsor as SponsorModel

router = RouterPaginated(tags=["Sponsors"])


class SponsorBase(Schema):
    """Base schema for Sponsor (used in list endpoints)."""

    image_url: str
    key: str
    name: str
    sponsor_type: str
    url: str


class Sponsor(SponsorBase):
    """Schema for Sponsor (minimal fields for list display)."""


class SponsorDetail(SponsorBase):
    """Detail schema for Sponsor (used in single item endpoints)."""

    description: str
    is_member: bool
    job_url: str
    member_type: str


class SponsorError(Schema):
    """Sponsor error schema."""

    message: str


class SponsorFilter(FilterSchema):
    """Filter for Sponsor."""

    is_member: bool | None = Field(
        None,
        description="Member status of the sponsor",
    )
    member_type: SponsorModel.MemberType | None = Field(
        None,
        description="Member type of the sponsor",
    )

    sponsor_type: str | None = Field(
        None,
        description=("Filter by the type of sponsorship (e.g., Gold, Silver, Platinum)."),
        example="Silver",
    )


class SponsorApplyRequest(Schema):
    """Request schema for sponsor application."""

    organization_name: str = Field(..., min_length=1, description="Organization name")
    website: str = Field("", description="Organization website URL")
    contact_email: str = Field(..., min_length=1, description="Contact email address")
    message: str = Field("", description="Sponsorship interest / message")


class SponsorApplyResponse(Schema):
    """Response schema for a successful sponsor application."""

    key: str
    message: str


@router.get(
    "/",
    description="Retrieve a paginated list of active OWASP sponsors.",
    operation_id="list_sponsors",
    response=list[Sponsor],
    summary="List sponsors",
)
@decorate_view(cache_response())
def list_sponsors(
    request: HttpRequest,
    filters: SponsorFilter = Query(...),
    ordering: Literal["name", "-name"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Sponsor]:
    """Get active sponsors."""
    qs = SponsorModel.objects.order_by(ordering or "name").filter(
        status=SponsorModel.Status.ACTIVE
    )
    return filters.filter(qs)


@router.get(
    "/{str:sponsor_id}",
    description="Retrieve sponsor details.",
    operation_id="get_sponsor",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: SponsorError,
        HTTPStatus.OK: SponsorDetail,
    },
    summary="Get sponsor",
)
@decorate_view(cache_response())
def get_sponsor(
    request: HttpRequest,
    sponsor_id: str = Path(..., example="adobe"),
) -> SponsorDetail | SponsorError:
    """Get a single active sponsor."""
    sponsor = SponsorModel.objects.filter(key__iexact=sponsor_id).first()
    if sponsor and sponsor.status == SponsorModel.Status.ACTIVE:
        return sponsor

    return Response({"message": "Sponsor not found"}, status=HTTPStatus.NOT_FOUND)


@router.post(
    "/apply",
    description=("Submit a sponsor application. Creates a draft record for admin review."),
    operation_id="apply_sponsor",
    response={
        HTTPStatus.CREATED: SponsorApplyResponse,
        HTTPStatus.BAD_REQUEST: SponsorError,
    },
    summary="Apply to become a sponsor",
)
def apply_sponsor(
    request: HttpRequest,
    payload: SponsorApplyRequest,
) -> tuple[int, SponsorApplyResponse | SponsorError]:
    """Create a draft sponsor application."""
    organization_name = payload.organization_name.strip()
    key = slugify(organization_name)

    if not key:
        return HTTPStatus.BAD_REQUEST, SponsorError(
            message=("Invalid organization name. Please include at least one letter or number.")
        )

    if SponsorModel.objects.filter(key=key).exists():
        return HTTPStatus.BAD_REQUEST, SponsorError(
            message=(f"An application for '{organization_name}' already exists.")
        )

    SponsorModel.objects.create(
        key=key,
        name=organization_name,
        sort_name=organization_name,
        contact_email=payload.contact_email,
        url=payload.website,
        description=payload.message,
        status=SponsorModel.Status.DRAFT,
    )

    return HTTPStatus.CREATED, SponsorApplyResponse(
        key=key,
        message=("Application received. The Nest team will review and follow up."),
    )
