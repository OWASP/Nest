"""Nest app User model admin."""

from django.contrib import admin

from apps.nest.models.user import User


class UserAdmin(admin.ModelAdmin):
    """Admin for User model."""

    autocomplete_fields = ("github_user",)
    ordering = ("username",)
    search_fields = ("email", "username")


admin.site.register(User, UserAdmin)
