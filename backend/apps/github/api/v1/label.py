"""Label API."""

from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import CACHE_TIME, PAGE_SIZE
from apps.github.models.label import Label

router = Router()


class LabelFilterSchema(FilterSchema):
    """Filter schema for Label."""

    color: str | None = None


class LabelSchema(Schema):
    """Schema for Label."""

    color: str
    description: str
    name: str


@router.get("/", response={200: list[LabelSchema], 404: dict})
@decorate_view(cache_page(CACHE_TIME))
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_label(
    request: HttpRequest, filters: LabelFilterSchema = Query(...)
) -> list[LabelSchema] | dict:
    """Get all labels."""
    labels = filters.filter(Label.objects.all())
    if not labels.exists():
        raise HttpError(404, "Labels not found")
    return labels
