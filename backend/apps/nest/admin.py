"""NEST app admin."""

from django.contrib import admin

from apps.nest.models.user import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ("username",)
    list_display = ("github_id",)
    ordering = ("username",)


admin.site.register(User, UserAdmin)
