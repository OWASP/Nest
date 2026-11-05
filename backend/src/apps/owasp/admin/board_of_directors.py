"""Board of Directors admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_of_directors import BoardOfDirectors


class BoardOfDirectorsAdmin(admin.ModelAdmin):
    """Admin for Snapshot model."""

    list_filter = ("year",)
    ordering = ("-year",)
    search_fields = ("year",)


admin.site.register(BoardOfDirectors, BoardOfDirectorsAdmin)
