"""Board meeting action admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_meeting_action import BoardMeetingAction


class BoardMeetingActionAdmin(admin.ModelAdmin):
    """Admin for BoardMeetingAction model."""

    list_display = ("meeting", "order", "discussion", "motion", "outcome")
    list_filter = ("meeting__type",)
    ordering = ("meeting", "order")
    raw_id_fields = ("meeting", "discussion", "motion", "outcome")
    search_fields = (
        "meeting__title",
        "discussion__topic",
        "motion__title",
        "outcome__description",
    )


admin.site.register(BoardMeetingAction, BoardMeetingActionAdmin)
