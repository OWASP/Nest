"""Committee API."""

from datetime import datetime

from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import CACHE_TIME, PAGE_SIZE
from apps.owasp.models.committee import Committee

router = Router()


class CommitteeFilterSchema(FilterSchema):
    """Filter schema for Committee."""

    name: str | None = None


class CommitteeSchema(Schema):
    """Schema for Committee."""

    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@router.get("/", response={200: list[CommitteeSchema], 404: dict})
@decorate_view(cache_page(CACHE_TIME))
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_committees(
    request: HttpRequest, filters: CommitteeFilterSchema = Query(...)
) -> list[CommitteeSchema] | dict:
    """Get all committees."""
    committees = filters.filter(Committee.objects.all())
    if not committees.exists():
        raise HttpError(404, "Committees not found")
    return committees
