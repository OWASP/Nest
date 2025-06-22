"""AI app admin."""

from django.contrib import admin

from apps.ai.models.chunk import Chunk


class ChunkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "chunk_text",
    )
    search_fields = (
        "message__slack_message_id",
        "chunk_text",
    )


admin.site.register(Chunk, ChunkAdmin)
