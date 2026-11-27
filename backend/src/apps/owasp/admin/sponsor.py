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
        "is_member",
        "member_type",
    )
    search_fields = (
        "name",
        "sort_name",
        "description",
    )
    list_filter = (
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
            "Status",
            {
                "fields": (
                    "is_member",
                    "member_type",
                    "sponsor_type",
                )
            },
        ),
    )


admin.site.register(Sponsor, SponsorAdmin)
