"""Chapter API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from apps.owasp.models.chapter import Chapter

router = Router()


class ChapterSchema(BaseModel):
    """Schema for Chapter."""

    model_config = {"from_attributes": True}

    country: str
    created_at: datetime
    name: str
    region: str
    updated_at: datetime


@router.get("/", response=list[ChapterSchema])
def get_chapters(request: HttpRequest) -> list[ChapterSchema]:
    """Get all chapters."""
    return Chapter.objects.all()
