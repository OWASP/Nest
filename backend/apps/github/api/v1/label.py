"""Label API."""

from django.http import HttpRequest
from ninja import Router, Schema

from apps.github.models.label import Label

router = Router()


class LabelSchema(Schema):
    """Schema for Label."""

    color: str
    description: str
    name: str


@router.get("/", response=list[LabelSchema])
def list_label(request: HttpRequest) -> list[LabelSchema]:
    """Get all labels."""
    return Label.objects.all()
