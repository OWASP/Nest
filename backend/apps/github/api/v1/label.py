"""Label API."""

from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja.pagination import RouterPaginated

from apps.github.models.label import Label

router = RouterPaginated()


class LabelSchema(Schema):
    """Schema for Label."""

    color: str
    description: str
    name: str


@router.get("/", response=list[LabelSchema])
def list_label(request: HttpRequest) -> list[LabelSchema]:
    """Get all labels."""
    labels = Label.objects.all()
    if not labels:
        raise HttpError(404, "Labels not found")
    return labels
