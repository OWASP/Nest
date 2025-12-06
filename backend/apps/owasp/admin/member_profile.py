"""Django admin configuration for MemberProfile model."""

from django.contrib import admin

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

    def get_queryset(self, request):
        """Return queryset with select_related github_user.

        Args:
            request (HttpRequest): The current admin request.

        Returns:
            QuerySet: Optimized queryset with prefetched relations.

        """
        queryset = super().get_queryset(request)
        return queryset.select_related("github_user")


admin.site.register(MemberProfile, MemberProfileAdmin)
