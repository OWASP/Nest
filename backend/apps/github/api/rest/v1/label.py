"""Label API."""

from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.label import Label

router = Router()


class LabelFilterSchema(FilterSchema):
    """Filter schema for Label."""

    color: str | None = Field(
        None,
        description="Color of the label",
        example="d93f0b",
    )


class LabelSchema(Schema):
    """Schema for Label."""

    color: str
    description: str
    name: str


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub labels.",
    operation_id="list_labels",
    response={200: list[LabelSchema]},
    summary="List labels",
    tags=["github"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_label(
    request: HttpRequest,
    filters: LabelFilterSchema = Query(...),
    ordering: Literal["nest_created_at", "-nest_created_at", "nest_updated_at", "-nest_updated_at"]
    | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[LabelSchema]:
    """Get all labels."""
    labels = filters.filter(Label.objects.all())

    if ordering:
        labels = labels.order_by(ordering)

    return labels
