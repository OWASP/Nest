"""Admin registration for SnapshotSubscription model."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class SnapshotSubscriptionAdminForm(forms.ModelForm):
    """Custom form for SnapshotSubscription admin to validate duplicates with M2M."""

    class Meta:
        """Meta options."""

        model = SnapshotSubscription
        fields = (
            "user",
            "name",
            "frequency",
            "is_active",
            "include_chapters",
            "include_events",
            "include_issues",
            "include_posts",
            "include_projects",
            "include_pull_requests",
            "include_releases",
            "include_users",
            "subscribed_projects",
            "subscribed_chapters",
            "subscribed_committees",
        )

    def clean(self):
        """Validate form data, including M2M fields, to check for duplicates."""
        cleaned_data = super().clean()

        user = cleaned_data.get("user")
        if not user:
            return cleaned_data

        other_subs = SnapshotSubscription.objects.filter(
            user=user,
            frequency=cleaned_data.get("frequency"),
            include_chapters=cleaned_data.get("include_chapters"),
            include_events=cleaned_data.get("include_events"),
            include_issues=cleaned_data.get("include_issues"),
            include_posts=cleaned_data.get("include_posts"),
            include_projects=cleaned_data.get("include_projects"),
            include_pull_requests=cleaned_data.get("include_pull_requests"),
            include_releases=cleaned_data.get("include_releases"),
            include_users=cleaned_data.get("include_users"),
        ).prefetch_related(
            "subscribed_projects",
            "subscribed_chapters",
            "subscribed_committees",
        )

        if self.instance and self.instance.pk:
            other_subs = other_subs.exclude(pk=self.instance.pk)

        if not other_subs.exists():
            return cleaned_data

        current_project_ids = {p.pk for p in (cleaned_data.get("subscribed_projects") or [])}
        current_chapter_ids = {c.pk for c in (cleaned_data.get("subscribed_chapters") or [])}
        current_committee_ids = {c.pk for c in (cleaned_data.get("subscribed_committees") or [])}

        duplicate_found = any(
            {p.pk for p in other.subscribed_projects.all()} == current_project_ids
            and {c.pk for c in other.subscribed_chapters.all()} == current_chapter_ids
            and {c.pk for c in other.subscribed_committees.all()} == current_committee_ids
            for other in other_subs
        )

        if duplicate_found:
            msg = "A subscription with the same configuration already exists."
            raise ValidationError(msg)

        return cleaned_data


class SnapshotSubscriptionAdmin(admin.ModelAdmin):
    """Admin for SnapshotSubscription model."""

    form = SnapshotSubscriptionAdminForm

    list_display = ("user", "name", "frequency", "is_active", "created_at", "updated_at")
    list_filter = ("frequency", "is_active", "created_at")
    search_fields = ("user__email", "user__username", "name")
    raw_id_fields = ("user",)
    readonly_fields = ("unsubscribe_token", "created_at", "updated_at")
    autocomplete_fields = ("subscribed_projects", "subscribed_chapters", "subscribed_committees")

    fieldsets = (
        (None, {"fields": ("user", "name", "frequency", "is_active")}),
        (
            "Content Toggles",
            {
                "fields": (
                    "include_chapters",
                    "include_events",
                    "include_issues",
                    "include_posts",
                    "include_projects",
                    "include_pull_requests",
                    "include_releases",
                    "include_users",
                ),
            },
        ),
        (
            "Subscribed Entities",
            {
                "fields": (
                    "subscribed_projects",
                    "subscribed_chapters",
                    "subscribed_committees",
                ),
            },
        ),
        (
            "System",
            {
                "fields": ("unsubscribe_token", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


admin.site.register(SnapshotSubscription, SnapshotSubscriptionAdmin)
