"""Chapter API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja.pagination import RouterPaginated

from apps.owasp.models.chapter import Chapter

router = RouterPaginated()


class ChapterSchema(Schema):
    """Schema for Chapter."""

    country: str
    created_at: datetime
    name: str
    region: str
    updated_at: datetime


@router.get("/", response=list[ChapterSchema])
def list_chapters(request: HttpRequest) -> list[ChapterSchema] | HttpError:
    """Get all chapters."""
    chapters = Chapter.objects.all()
    if not chapters:
        raise HttpError(404, "Chapters not found")
    return chapters
