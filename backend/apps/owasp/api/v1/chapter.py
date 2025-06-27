"""Chapter API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

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
@paginate(PageNumberPagination, page_size=100)
def list_chapters(request: HttpRequest) -> list[ChapterSchema]:
    """Get all chapters."""
    chapters = Chapter.objects.all()
    if not chapters:
        raise HttpError(404, "Chapters not found")
    return chapters
