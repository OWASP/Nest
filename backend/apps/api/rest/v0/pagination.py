"""Common pagination classes for v0 API."""

from typing import Any

from django.http import Http404
from ninja import Field, Schema
from ninja.pagination import PaginationBase


class CustomPagination(PaginationBase):
    """Custom pagination with standardized output schema."""

    items_attribute: str = "items"

    class Input(Schema):
        """Input parameters for pagination."""

        page: int = Field(1, ge=1, description="Page number")
        page_size: int = Field(100, ge=1, le=100, description="Number of items per page")

    class Output(Schema):
        """Standardized output schema for paginated responses."""

        current_page: int = Field(description="Current page number")
        has_next: bool = Field(description="Whether there is a next page")
        has_previous: bool = Field(description="Whether there is a previous page")
        items: list[Any] = Field(description="List of items")
        total_count: int = Field(description="Total number of items")
        total_pages: int = Field(description="Total number of pages")

    def paginate_queryset(self, queryset, pagination: Input, **params):
        """Paginate the queryset and return standardized output."""
        page = pagination.page
        page_size = pagination.page_size
        total_count = queryset.count()
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        if page > total_pages:
            message = f"Page {page} not found. Valid pages are 1 to {total_pages}."
            raise Http404(message)

        offset = (page - 1) * page_size

        items = list(queryset[offset : offset + page_size])

        return {
            "current_page": page,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "items": items,
            "total_count": total_count,
            "total_pages": total_pages,
        }
