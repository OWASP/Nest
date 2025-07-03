"""AI app admin."""

from django.contrib import admin

from apps.ai.models.chunk import Chunk


class ChunkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
        "content_type",
    )
    search_fields = ("text", "object_id")


admin.site.register(Chunk, ChunkAdmin)
