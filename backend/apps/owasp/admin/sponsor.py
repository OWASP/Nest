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
        "chapter",
        "project",
    )
    search_fields = (
        "name",
        "sort_name",
        "description",
        "contact_email",
    )
    list_filter = (
        "sponsor_type",
        "status",
        "is_member",
        "member_type",
        "chapter",
        "project",
    )
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "sort_name",
                    "description",
                    "contact_email",
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
            "Status",
            {
                "fields": (
                    "is_member",
                    "member_type",
                    "sponsor_type",
                    "status",
                )
            },
        ),
        (
            "Entity Associations",
            {
                "fields": (
                    "chapter",
                    "project",
                ),
                "description": (
                    "Optional: Link this sponsor to a specific chapter or project. "
                    "Leave blank for global sponsors."
                ),
            },
        ),
    )
    readonly_fields = ("nest_created_at", "nest_updated_at")


admin.site.register(Sponsor, SponsorAdmin)
