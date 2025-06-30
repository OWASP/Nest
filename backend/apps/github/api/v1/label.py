"""Label API."""

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.label import Label

router = Router()


class LabelSchema(Schema):
    """Schema for Label."""

    color: str
    description: str
    name: str


@router.get("/", response={200: list[LabelSchema], 404: dict})
@paginate(PageNumberPagination, page_size=100)
def list_label(request: HttpRequest) -> list[LabelSchema] | dict:
    """Get all labels."""
    labels = Label.objects.all()
    if not labels.exists():
        raise HttpError(404, "Labels not found")
    return labels
