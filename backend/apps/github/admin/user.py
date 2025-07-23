"""GitHub app User model admin."""

from django.contrib import admin

from apps.github.models.user import User


class UserAdmin(admin.ModelAdmin):
    """Admin for User model."""

    list_display = (
        "title",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "login",
        "name",
    )


admin.site.register(User, UserAdmin)
