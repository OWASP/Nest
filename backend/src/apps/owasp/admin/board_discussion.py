"""Board discussion admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_discussion import BoardDiscussion


class BoardDiscussionAdmin(admin.ModelAdmin):
    """Admin for BoardDiscussion model."""

    autocomplete_fields = ("participants",)
    list_display = ("topic",)
    search_fields = ("topic", "description")


admin.site.register(BoardDiscussion, BoardDiscussionAdmin)
