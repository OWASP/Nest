"""Committee API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Path, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate
from ninja.responses import Response

from apps.owasp.models.committee import Committee

router = Router()


class CommitteeErrorResponse(Schema):
    """Committee error response schema."""

    message: str


class CommitteeSchema(Schema):
    """Schema for Committee."""

    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP committees.",
    operation_id="list_committees",
    response={200: list[CommitteeSchema]},
    summary="List committees",
    tags=["Committees"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_committees(
    request: HttpRequest,
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[CommitteeSchema]:
    """Get committees."""
    return Committee.active_committees.order_by(ordering or "-created_at")


@router.get(
    "/{str:committee_id}",
    description="Retrieve committee details.",
    operation_id="get_committee",
    response={
        HTTPStatus.NOT_FOUND: CommitteeErrorResponse,
        HTTPStatus.OK: CommitteeSchema,
    },
    summary="Get committee",
    tags=["Committees"],
)
def get_chapter(
    request: HttpRequest,
    committee_id: str = Path(example="project"),
) -> CommitteeSchema | CommitteeErrorResponse:
    """Get chapter."""
    if committee := Committee.active_committees.filter(
        is_active=True,
        key__iexact=(
            committee_id
            if committee_id.startswith("www-committee-")
            else f"www-committee-{committee_id}"
        ),
    ).first():
        return committee

    return Response({"message": "Committee not found"}, status=HTTPStatus.NOT_FOUND)
