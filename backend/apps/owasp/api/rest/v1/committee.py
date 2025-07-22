"""Committee API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.committee import Committee

router = Router()


class CommitteeFilterSchema(FilterSchema):
    """Filter schema for Committee."""


class CommitteeSchema(Schema):
    """Schema for Committee."""

    name: str
    description: str
    created_at: datetime
    updated_at: datetime


VALID_COMMITTEE_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get("/", response={200: list[CommitteeSchema]})
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_committees(
    request: HttpRequest,
    filters: CommitteeFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[CommitteeSchema]:
    """Get all committees."""
    committees = filters.filter(Committee.objects.all())

    if ordering and ordering in VALID_COMMITTEE_ORDERING_FIELDS:
        committees = committees.order_by(ordering)

    return committees
