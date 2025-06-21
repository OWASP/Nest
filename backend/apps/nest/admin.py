"""Nest app admin."""

from django.contrib import admin

from apps.nest.models.user import User


class UserAdmin(admin.ModelAdmin):
    ordering = ("username",)
    search_fields = ("email", "username")


admin.site.register(User, UserAdmin)
