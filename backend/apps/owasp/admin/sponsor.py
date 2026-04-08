"""Sponsor admin configuration."""

from django.contrib import admin

from apps.owasp.models.sponsor import Sponsor

from .mixins import StandardOwaspAdminMixin


class SponsorAdmin(admin.ModelAdmin, StandardOwaspAdminMixin):
    """Admin for Sponsor model."""

    actions = ("activate_sponsors", "archive_sponsors")
    list_display = (
        "name",
        "status",
        "sponsor_type",
        "contact_email",
        "is_member",
        "member_type",
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
                    "status",
                    "is_member",
                    "member_type",
                    "sponsor_type",
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
                "classes": ("collapse",),
            },
        ),
    )

    @admin.action(description="Activate selected sponsors")
    def activate_sponsors(self, request, queryset) -> None:
        """Set selected sponsors to active status."""
        updated = queryset.update(status=Sponsor.Status.ACTIVE)
        self.message_user(request, f"{updated} sponsor(s) marked as active.")

    @admin.action(description="Archive selected sponsors")
    def archive_sponsors(self, request, queryset) -> None:
        """Set selected sponsors to archived status."""
        updated = queryset.update(status=Sponsor.Status.ARCHIVED)
        self.message_user(request, f"{updated} sponsor(s) archived.")


admin.site.register(Sponsor, SponsorAdmin)
