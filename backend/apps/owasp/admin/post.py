from django.contrib import admin

from apps.owasp.models.post import Post


class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model."""

    list_display = (
        "author_name",
        "published_at",
        "title",
    )
    search_fields = (
        "author_image_url",
        "author_name",
        "published_at",
        "title",
        "url",
    )


admin.site.register(Post, PostAdmin)
