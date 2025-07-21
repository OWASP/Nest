"""Project API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.project import Project

router = Router()


class ProjectFilterSchema(FilterSchema):
    """Filter schema for Project."""

    level: str | None = None


class ProjectSchema(Schema):
    """Schema for Project."""

    created_at: datetime
    description: str
    level: str
    name: str
    updated_at: datetime


VALID_PROJECT_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get("/", response={200: list[ProjectSchema]})
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_projects(
    request: HttpRequest,
    filters: ProjectFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[ProjectSchema]:
    """Get all projects."""
    projects = filters.filter(Project.objects.all())

    if ordering and ordering in VALID_PROJECT_ORDERING_FIELDS:
        projects = projects.order_by(ordering)

    return projects
