"""Sponsor API."""

from http import HTTPStatus
from typing import Literal

from django.db import IntegrityError, transaction
from django.db.models import Case, IntegerField, Value, When
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

    description: str
    image_url: str
    key: str
    name: str
    sponsor_type: str
    url: str


class Sponsor(SponsorBase):
    """Schema for Sponsor (minimal fields for list display)."""


class SponsorDetail(SponsorBase):
    """Detail schema for Sponsor (used in single item endpoints)."""

    is_member: bool
    job_url: str
    member_type: str
    status: str


class SponsorError(Schema):
    """Sponsor error schema."""

    message: str


class SponsorApplication(Schema):
    """Schema for sponsor application form submission."""

    organization_name: str = Field(..., description="Name of the sponsoring organization")
    website: str = Field("", description="Organization website URL")
    contact_email: str = Field(..., description="Contact email address")
    message: str = Field("", description="Sponsorship interest or message")


class SponsorApplicationResponse(Schema):
    """Response schema for sponsor application."""

    message: str
    key: str


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

    status: str | None = Field(
        None,
        description="Filter by sponsor status (draft, active, archived). Defaults to active.",
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
    qs = SponsorModel.objects.order_by(ordering or "name")
    if filters.status is None:
        qs = qs.filter(status=SponsorModel.SponsorStatus.ACTIVE)

    return filters.filter(qs)


@router.get(
    "/nest",
    description="Retrieve active OWASP Nest sponsors for external integrations.",
    operation_id="list_nest_sponsors",
    response=list[Sponsor],
    summary="List Nest sponsors",
)
@decorate_view(cache_response())
def list_nest_sponsors(
    request: HttpRequest,
) -> list[Sponsor]:
    """Get active Nest sponsors for external integrations (GitHub Actions, dashboards, etc.)."""
    tier_order = Case(
        When(sponsor_type=SponsorModel.SponsorType.DIAMOND, then=Value(1)),
        When(sponsor_type=SponsorModel.SponsorType.PLATINUM, then=Value(2)),
        When(sponsor_type=SponsorModel.SponsorType.GOLD, then=Value(3)),
        When(sponsor_type=SponsorModel.SponsorType.SILVER, then=Value(4)),
        When(sponsor_type=SponsorModel.SponsorType.SUPPORTER, then=Value(5)),
        default=Value(6),
        output_field=IntegerField(),
    )
    return list(
        SponsorModel.objects.filter(status=SponsorModel.SponsorStatus.ACTIVE)
        .annotate(tier_order=tier_order)
        .order_by("tier_order", "name")
    )


@router.post(
    "/apply",
    description="Submit a sponsor application. Creates a new sponsor record with draft status.",
    operation_id="apply_sponsor",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.CREATED: SponsorApplicationResponse,
    },
    summary="Apply to become a sponsor",
)
def apply_sponsor(
    request: HttpRequest,
    payload: SponsorApplication,
) -> Response:
    """Submit a sponsor application."""
    key = slugify(payload.organization_name)

    if not key:
        return Response(
            {"message": "Organization name must produce a valid key."},
            status=HTTPStatus.BAD_REQUEST,
        )

    duplicate_response = Response(
        {"message": "A sponsor application with this organization name already exists."},
        status=HTTPStatus.BAD_REQUEST,
    )

    try:
        with transaction.atomic():
            SponsorModel.objects.create(
                contact_email=payload.contact_email,
                description=payload.message,
                key=key,
                name=payload.organization_name,
                sort_name=payload.organization_name,
                status=SponsorModel.SponsorStatus.DRAFT,
                url=payload.website,
            )
    except IntegrityError:
        return duplicate_response

    return Response(
        {
            "message": "Sponsor application submitted successfully. "
            "It will be reviewed by the OWASP team.",
            "key": key,
        },
        status=HTTPStatus.CREATED,
    )


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
