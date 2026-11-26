"""Board outcome admin configuration."""

from django.contrib import admin
from django.db.models import F, QuerySet

from apps.owasp.models.board_outcome import BoardOutcome


class BoardOutcomeAdmin(admin.ModelAdmin):
    """Admin for BoardOutcome model."""

    autocomplete_fields = ("assignees",)
    list_display = ("description", "status", "due_date")
    list_filter = ("status",)
    search_fields = ("description",)

    def get_queryset(self, request) -> QuerySet:
        """Order dated outcomes first, keeping null due dates last."""
        return super().get_queryset(request).order_by(F("due_date").desc(nulls_last=True))


admin.site.register(BoardOutcome, BoardOutcomeAdmin)
