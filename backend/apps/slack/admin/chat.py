"""Chat admin configuration."""

from django.contrib import admin

from apps.slack.models.chat import Chat


class ChatAdmin(admin.ModelAdmin):
    """Admin for Chat model."""

    list_display = ("user", "workspace", "created_at")
    list_filter = ("user", "workspace")
    search_fields = ("user__username", "workspace__name")


admin.site.register(Chat, ChatAdmin)
