"""Committee API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import ValidationErrorSchema
from apps.owasp.models.committee import Committee as CommitteeModel

router = RouterPaginated(tags=["Committees"])


class CommitteeBase(Schema):
    """Base schema for Committee (used in list endpoints)."""

    created_at: datetime
    key: str
    name: str
    updated_at: datetime

    @staticmethod
    def resolve_key(obj: CommitteeModel) -> str:
        """Resolve key."""
        return obj.nest_key


class Committee(CommitteeBase):
    """Schema for Committee (minimal fields for list display)."""


class CommitteeDetail(CommitteeBase):
    """Detail schema for Committee (used in single item endpoints)."""

    description: str


class CommitteeError(Schema):
    """Committee error schema."""

    message: str


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP committees.",
    operation_id="list_committees",
    response=list[Committee],
    summary="List committees",
)
@decorate_view(cache_response())
def list_committees(
    request: HttpRequest,
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Committee]:
    """Get committees."""
    return CommitteeModel.active_committees.order_by(ordering or "-created_at")


@router.get(
    "/{str:committee_id}",
    description="Retrieve committee details.",
    operation_id="get_committee",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: CommitteeError,
        HTTPStatus.OK: CommitteeDetail,
    },
    summary="Get committee",
)
@decorate_view(cache_response())
def get_committee(
    request: HttpRequest,
    committee_id: str = Path(example="project"),
) -> CommitteeDetail | CommitteeError:
    """Get committee."""
    if committee := CommitteeModel.active_committees.filter(
        is_active=True,
        key__iexact=(
            committee_id
            if committee_id.startswith("www-committee-")
            else f"www-committee-{committee_id}"
        ),
    ).first():
        return committee

    return Response({"message": "Committee not found"}, status=HTTPStatus.NOT_FOUND)
