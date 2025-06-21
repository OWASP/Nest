"""Label API."""

from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from apps.github.models.label import Label

router = Router()


class LabelSchema(BaseModel):
    """Schema for Label."""

    model_config = {"from_attributes": True}

    color: str
    description: str
    name: str


@router.get("/", response=list[LabelSchema])
def get_label(request: HttpRequest) -> list[LabelSchema]:
    """Get all labels."""
    return Label.objects.all()
