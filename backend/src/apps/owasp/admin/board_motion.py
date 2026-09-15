"""Board motion admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_motion import BoardMotion


class BoardMotionAdmin(admin.ModelAdmin):
    """Admin for BoardMotion model."""

    list_display = ("title", "sponsor", "second")
    raw_id_fields = ("sponsor", "second", "amends_motion")
    search_fields = ("title", "description", "background")


admin.site.register(BoardMotion, BoardMotionAdmin)
