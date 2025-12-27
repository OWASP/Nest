"""Django admin configuration for MemberSnapshot model."""

from django.contrib import admin

from apps.owasp.models.member_snapshot import MemberSnapshot


class MemberSnapshotAdmin(admin.ModelAdmin):
    """Admin for MemberSnapshot model."""

    autocomplete_fields = (
        "github_user",
        "commits",
        "pull_requests",
        "issues",
        "messages",
    )
    list_display = (
        "github_user",
        "start_at",
        "end_at",
        "commits_count",
        "pull_requests_count",
        "issues_count",
        "messages_count",
        "total_contributions",
        "nest_created_at",
    )
    list_filter = (
        "start_at",
        "end_at",
        "nest_created_at",
    )
    search_fields = (
        "github_user__login",
        "github_user__name",
    )
    readonly_fields = (
        "commits_count",
        "pull_requests_count",
        "issues_count",
        "messages_count",
        "total_contributions",
        "contribution_heatmap_data",
        "communication_heatmap_data",
        "chapter_contributions",
        "project_contributions",
        "repository_contributions",
        "channel_communications",
        "nest_created_at",
        "nest_updated_at",
    )
    date_hierarchy = "start_at"

    fieldsets = (
        (
            "Snapshot Information",
            {
                "fields": (
                    "github_user",
                    "start_at",
                    "end_at",
                )
            },
        ),
        (
            "GitHub Contributions",
            {
                "fields": (
                    "commits",
                    "pull_requests",
                    "issues",
                )
            },
        ),
        (
            "Slack Communications",
            {"fields": ("messages",)},
        ),
        (
            "Statistics",
            {
                "fields": (
                    "commits_count",
                    "pull_requests_count",
                    "issues_count",
                    "messages_count",
                    "total_contributions",
                    "contribution_heatmap_data",
                    "communication_heatmap_data",
                    "chapter_contributions",
                    "project_contributions",
                    "repository_contributions",
                    "channel_communications",
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
        """Return the queryset for the admin list view.

        Args:
            request (HttpRequest): The current admin request.

        Returns:
            QuerySet: QuerySet with related github_user included.

        """
        queryset = super().get_queryset(request)
        return queryset.select_related("github_user")


admin.site.register(MemberSnapshot, MemberSnapshotAdmin)
