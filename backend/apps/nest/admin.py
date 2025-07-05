"""Nest app admin."""

from django.contrib import admin

from apps.nest.models.apikey import APIKey
from apps.nest.models.user import User


class UserAdmin(admin.ModelAdmin):
    ordering = ("username",)
    search_fields = ("email", "username")


class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "key_suffix", "revoked", "expires_at", "created_at")
    search_fields = ("name", "user__username", "key_suffix")
    list_filter = ("revoked", "expires_at", "created_at")
    ordering = ("-created_at",)


admin.site.register(APIKey, APIKeyAdmin)

admin.site.register(User, UserAdmin)
