"""Label API."""

from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated

from apps.github.models.label import Label as LabelModel

router = RouterPaginated(tags=["Labels"])


class LabelBase(Schema):
    """Base schema for Label (used in list endpoints)."""

    color: str
    name: str


class Label(LabelBase):
    """Schema for Label (minimal fields for list display)."""


class LabelDetail(LabelBase):
    """Detail schema for Label (used in single item endpoints)."""

    description: str


class LabelFilter(FilterSchema):
    """Filter for Label."""

    color: str | None = Field(
        None,
        description="Color of the label",
        example="d93f0b",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub labels.",
    operation_id="list_labels",
    response=list[Label],
    summary="List labels",
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
def list_label(
    request: HttpRequest,
    filters: LabelFilter = Query(...),
    ordering: Literal["nest_created_at", "-nest_created_at", "nest_updated_at", "-nest_updated_at"]
    | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Label]:
    """Get all labels."""
    labels = filters.filter(LabelModel.objects.all())

    if ordering:
        labels = labels.order_by(ordering)

    return labels
