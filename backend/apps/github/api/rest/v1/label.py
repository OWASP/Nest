"""Label API."""

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

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


VALID_LABEL_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get(
    "/",
    summary="Get all labels",
    tags=["Labels"],
    response={200: list[LabelSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_label(
    request: HttpRequest,
    filters: LabelFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[LabelSchema]:
    """Get all labels."""
    labels = filters.filter(Label.objects.all())

    if ordering and ordering in VALID_LABEL_ORDERING_FIELDS:
        labels = labels.order_by(ordering)

    return labels
