"""Committee API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

from apps.owasp.models.committee import Committee

router = Router()


class CommitteeSchema(Schema):
    """Schema for Committee."""

    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@router.get("/", response=list[CommitteeSchema])
def list_committees(request: HttpRequest) -> list[CommitteeSchema]:
    """Get all committees."""
    return Committee.objects.all()
