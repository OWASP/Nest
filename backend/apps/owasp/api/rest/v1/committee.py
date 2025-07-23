"""Committee API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.committee import Committee

router = Router()


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
    summary="Get all committees",
    tags=["Committees"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_committees(
    request: HttpRequest,
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None, description="Ordering field"
    ),
) -> list[CommitteeSchema]:
    """Get all committees."""
    committees = Committee.objects.all()

    if ordering:
        committees = committees.order_by(ordering)

    return committees
