"""Django admin configuration for MemberProfile model."""

from django.contrib import admin
from django.db import models

from apps.owasp.models.member_profile import MemberProfile


class MemberProfileAdmin(admin.ModelAdmin):
    """Admin for MemberProfile model."""

    autocomplete_fields = ("github_user",)
    list_display = (
        "github_user",
        "owasp_slack_id",
        "first_contribution_at",
        "is_owasp_board_member",
        "is_former_owasp_staff",
        "is_gsoc_mentor",
        "nest_created_at",
    )
    list_filter = (
        "is_owasp_board_member",
        "is_former_owasp_staff",
        "is_gsoc_mentor",
        "nest_created_at",
    )
    search_fields = (
        "github_user__login",
        "github_user__name",
        "owasp_slack_id",
    )
    readonly_fields = (
        "nest_created_at",
        "nest_updated_at",
    )

    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "github_user",
                    "linkedin_page_id",
                    "owasp_slack_id",
                )
            },
        ),
        (
            "Contribution Information",
            {"fields": ("first_contribution_at",)},
        ),
        (
            "Membership Flags",
            {
                "fields": (
                    "is_owasp_board_member",
                    "is_former_owasp_staff",
                    "is_gsoc_mentor",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "nest_created_at",
                    "nest_updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request) -> models.QuerySet:
        """Retrieve optimized queryset with related GitHub user.

        Applies select_related on github_user to reduce database queries when displaying
        member profile lists.

        Args:
            request: The HTTP request object.

        Returns:
            QuerySet: MemberProfile queryset with prefetched github_user relations.

        """
        return super().get_queryset(request).select_related("github_user")


admin.site.register(MemberProfile, MemberProfileAdmin)
