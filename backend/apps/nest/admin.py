"""NEST app admin."""

from django.contrib import admin

from apps.nest.models.user import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ("username",)
    ordering = ("username",)


admin.site.register(User, UserAdmin)
