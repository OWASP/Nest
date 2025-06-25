"""Chapter API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

from apps.owasp.models.chapter import Chapter

router = Router()


class ChapterSchema(Schema):
    """Schema for Chapter."""

    country: str
    created_at: datetime
    name: str
    region: str
    updated_at: datetime


@router.get("/", response=list[ChapterSchema])
def list_chapters(request: HttpRequest) -> list[ChapterSchema]:
    """Get all chapters."""
    return Chapter.objects.all()
