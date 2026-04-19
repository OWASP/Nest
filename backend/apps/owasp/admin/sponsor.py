"""Sponsor admin configuration."""

from django.contrib import admin

from apps.owasp.models.sponsor import Sponsor

from .mixins import StandardOwaspAdminMixin


class SponsorAdmin(admin.ModelAdmin, StandardOwaspAdminMixin):
    """Admin for Sponsor model."""

    list_display = (
        "name",
        "sort_name",
        "sponsor_type",
        "status",
        "is_member",
        "member_type",
        "contact_email",
    )
    search_fields = (
        "name",
        "sort_name",
        "description",
        "contact_email",
    )
    list_filter = (
        "status",
        "sponsor_type",
        "is_member",
        "member_type",
    )
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "sort_name",
                    "description",
                )
            },
        ),
        (
            "URLs and Images",
            {
                "fields": (
                    "url",
                    "job_url",
                    "image_url",
                )
            },
        ),
        (
            "Contact",
            {"fields": ("contact_email",)},
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "is_member",
                    "member_type",
                    "sponsor_type",
                )
            },
        ),
        (
            "Entity Association",
            {
                "fields": (
                    "chapter",
                    "project",
                ),
                "description": (
                    "Optionally associate this sponsor with a specific chapter or project. "
                    "Leave blank for global/general sponsors."
                ),
            },
        ),
    )


admin.site.register(Sponsor, SponsorAdmin)
