"""GitHub app Comment model admin."""

from django.contrib import admin

from apps.github.models import Comment


class CommentAdmin(admin.ModelAdmin):
    """Admin for Comment model."""

    list_display = (
        "body",
        "author",
        "nest_created_at",
        "nest_updated_at",
    )
    list_filter = ("nest_created_at", "nest_updated_at")
    search_fields = ("body", "author__login")


admin.site.register(Comment, CommentAdmin)
