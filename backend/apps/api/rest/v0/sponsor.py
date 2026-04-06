"""Sponsor API."""

import logging
from http import HTTPStatus
from typing import Literal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import ValidationErrorSchema
from apps.common.utils import slugify
from apps.owasp.models.sponsor import Sponsor as SponsorModel

logger = logging.getLogger(__name__)

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


class SponsorApplicationRequest(Schema):
    """Schema for sponsor application request."""

    name: str = Field(..., description="Organization name")
    contact_email: str = Field(..., description="Contact email")
    website: str | None = Field(None, description="Organization website (optional)")
    sponsorship_interest: str = Field(..., description="Message about sponsorship interest")


class SponsorApplicationResponse(Schema):
    """Schema for sponsor application response."""

    id: int
    name: str
    status: str


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
        description="Filter by the type of sponsorship (e.g., Gold, Silver, Platinum).",
        example="Silver",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP sponsors.",
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
    """Get sponsors."""
    return filters.filter(SponsorModel.objects.order_by(ordering or "name"))


@router.get(
    "/{str:sponsor_id}",
    description="Retrieve a sponsor details.",
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
    """Get sponsor."""
    if sponsor := SponsorModel.objects.filter(key__iexact=sponsor_id).first():
        return sponsor

    return Response({"message": "Sponsor not found"}, status=HTTPStatus.NOT_FOUND)


@router.post(
    "/applications/",
    description="Submit a sponsor application.",
    operation_id="create_sponsor_application",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.CREATED: SponsorApplicationResponse,
    },
    summary="Create sponsor application",
)
def create_sponsor_application(
    request: HttpRequest,
    payload: SponsorApplicationRequest,
) -> Response:
    """Create a sponsor application."""
    try:
        name = payload.name.strip()
        contact_email = payload.contact_email.strip()
        sponsorship_interest = payload.sponsorship_interest.strip()
        website = (payload.website or "").strip()

        if not name or not contact_email or not sponsorship_interest:
            return Response(
                {"message": "Name, contact email, and sponsorship interest are required"},
                status=HTTPStatus.BAD_REQUEST,
            )

        key = slugify(name)
        if not key:
            return Response(
                {"message": "Organization name is invalid"},
                status=HTTPStatus.BAD_REQUEST,
            )

        if SponsorModel.objects.filter(key=key).exists():
            return Response(
                {"message": "A sponsor with this organization name already exists"},
                status=HTTPStatus.BAD_REQUEST,
            )

        sponsor = SponsorModel(
            name=name,
            key=key,
            contact_email=contact_email,
            url=website,
            description=sponsorship_interest,
            status=SponsorModel.Status.DRAFT,
            sort_name=name,
        )
        sponsor.full_clean()
        sponsor.save()

        return Response(
            SponsorApplicationResponse(
                id=sponsor.id,
                name=sponsor.name,
                status=sponsor.status,
            ),
            status=HTTPStatus.CREATED,
        )
    except (ValueError, ValidationError, IntegrityError) as e:
        logger.warning("Error creating sponsor application: %s", e)
        return Response(
            {"message": "Error creating sponsor application"},
            status=HTTPStatus.BAD_REQUEST,
        )
