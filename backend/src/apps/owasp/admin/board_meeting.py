"""Board meeting admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_meeting import BoardMeeting


class BoardMeetingAdmin(admin.ModelAdmin):
    """Admin for BoardMeeting model."""

    autocomplete_fields = ("board",)
    filter_horizontal = ("attendees", "absentees")
    list_display = ("title", "date", "board", "type", "quorum_present")
    list_filter = ("type", "quorum_present", "board__year")
    ordering = ("-date",)
    search_fields = ("title", "location", "source_path")


admin.site.register(BoardMeeting, BoardMeetingAdmin)
