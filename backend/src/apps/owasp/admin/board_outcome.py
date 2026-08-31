"""Board outcome admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_outcome import BoardOutcome


class BoardOutcomeAdmin(admin.ModelAdmin):
    """Admin for BoardOutcome model."""

    filter_horizontal = ("assignees",)
    list_display = ("description", "status", "due_date")
    list_filter = ("status",)
    ordering = ("-due_date",)
    search_fields = ("description",)


admin.site.register(BoardOutcome, BoardOutcomeAdmin)
