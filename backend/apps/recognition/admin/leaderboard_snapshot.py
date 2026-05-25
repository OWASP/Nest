"""Django admin configuration for LeaderboardSnapshot model."""

from django.contrib import admin

from apps.recognition.models.leaderboard_snapshot import LeaderboardSnapshot


@admin.register(LeaderboardSnapshot)
class LeaderboardSnapshotAdmin(admin.ModelAdmin):
    """Admin for LeaderboardSnapshot model."""

    autocomplete_fields = ("github_user", "project")
    list_display = (
        "github_user",
        "snapshot_date",
        "global_rank",
        "project_rank",
        "score",
        "tier",
        "project",
    )
    list_filter = ("tier", "snapshot_date", "project")
    search_fields = ("github_user__login", "github_user__name", "project__name")
    readonly_fields = ("nest_created_at", "nest_updated_at")

    fieldsets = (
        (
            "Contributor Information",
            {
                "fields": ("github_user", "project"),
            },
        ),
        (
            "Ranking Data",
            {
                "fields": ("snapshot_date", "global_rank", "project_rank"),
            },
        ),
        (
            "Score Information",
            {
                "fields": ("score", "tier"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("nest_created_at", "nest_updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
