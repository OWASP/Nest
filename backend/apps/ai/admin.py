"""AI app admin."""

from django.contrib import admin

from apps.ai.models.chunk import Chunk


class ChunkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "text",
    )
    search_fields = (
        "message__slack_message_id",
        "text",
    )


admin.site.register(Chunk, ChunkAdmin)
