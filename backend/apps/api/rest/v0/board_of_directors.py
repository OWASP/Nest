"""Board of Directors API."""

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

from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember

router = Router()


class BoardOfDirectorsErrorResponse(Schema):
    """Board error response schema."""

    message: str


class BoardFilterSchema(FilterSchema):
    """Filter schema for Board of Directors."""

    year: int | None = Field(None, description="Filter by year", example=2025)


class EntityMemberSchema(Schema):
    """Schema for EntityMember nested in board endpoints."""

    member_name: str
    member_email: str
    role: str
    order: int
    is_active: bool
    is_reviewed: bool


class BoardOfDirectorsSchema(Schema):
    """Schema for Board of Directors with nested members and candidates."""

    year: int
    created_at: datetime
    updated_at: datetime
    members: list[EntityMemberSchema]
    candidates: list[EntityMemberSchema]


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP Board of Directors.",
    operation_id="list_boards",
    response={200: list[BoardOfDirectorsSchema]},
    summary="List boards",
    tags=["Board of Directors"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_boards(
    request: HttpRequest,
    filters: BoardFilterSchema = Query(...),
    ordering: Literal["year", "-year", "created_at", "-created_at", "updated_at", "-updated_at"]
    | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[BoardOfDirectorsSchema]:
    """Get boards of directors with optional year filtering."""
    queryset = BoardOfDirectors.objects.all()

    # Apply filters
    if filters.year:
        queryset = queryset.filter(year=filters.year)

    return queryset.order_by(ordering or "-year")


@router.get(
    "/{int:year}",
    description="Retrieve Board of Directors details for a specific year.",
    operation_id="get_board",
    response={
        HTTPStatus.NOT_FOUND: BoardOfDirectorsErrorResponse,
        HTTPStatus.OK: BoardOfDirectorsSchema,
    },
    summary="Get board by year",
    tags=["Board of Directors"],
)
def get_board(
    request: HttpRequest,
    year: int = Path(example=2025),
) -> BoardOfDirectorsSchema | BoardOfDirectorsErrorResponse:
    """Get board by year including nested members and candidates."""
    if board := BoardOfDirectors.objects.filter(year=year).first():
        # Filter EntityMember by entity pointing to BoardOfDirectors
        members_qs = EntityMember.objects.filter(
            entity_type__model="boardofdirectors", entity_id=board.id
        )

        members = [
            {
                "member_name": m.member_name,
                "member_email": m.member_email,
                "role": m.role,
                "order": m.order,
                "is_active": m.is_active,
                "is_reviewed": m.is_reviewed,
            }
            for m in members_qs.filter(role=EntityMember.Role.MEMBER).order_by("order")
        ]

        candidates = [
            {
                "member_name": m.member_name,
                "member_email": m.member_email,
                "role": m.role,
                "order": m.order,
                "is_active": m.is_active,
                "is_reviewed": m.is_reviewed,
            }
            for m in members_qs.filter(role=EntityMember.Role.CANDIDATE).order_by("order")
        ]

        # Return dict matching BoardOfDirectorsSchema structure
        return {  # type: ignore[return-value]
            "year": board.year,
            "created_at": board.created_at,
            "updated_at": board.updated_at,
            "members": members,
            "candidates": candidates,
        }

    return Response({"message": "Board not found"}, status=HTTPStatus.NOT_FOUND)
