"""Committee API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.committee import Committee

router = Router()


class CommitteeSchema(Schema):
    """Schema for Committee."""

    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@router.get("/", response=list[CommitteeSchema])
@paginate(PageNumberPagination, page_size=100)
def list_committees(request: HttpRequest) -> list[CommitteeSchema]:
    """Get all committees."""
    committees = Committee.objects.all()
    if not committees:
        raise HttpError(404, "Committees not found")
    return committees
