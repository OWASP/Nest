"""Mentorship app Admin model admin."""

from django.contrib import admin

from apps.mentorship.models.admin import Admin


class AdminAdmin(admin.ModelAdmin):
    """Admin view for Admin model."""

    autocomplete_fields = (
        "github_user",
        "nest_user",
    )

    list_display = ("github_user",)

    search_fields = (
        "github_user__login",
        "github_user__name",
    )


admin.site.register(Admin, AdminAdmin)
