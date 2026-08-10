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

        duplicate_found = SnapshotSubscription.check_duplicate_setup(
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
            entity_ids={
                "projects": [p.pk for p in (cleaned_data.get("subscribed_projects") or [])],
                "chapters": [c.pk for c in (cleaned_data.get("subscribed_chapters") or [])],
                "committees": [c.pk for c in (cleaned_data.get("subscribed_committees") or [])],
            },
            exclude_pk=self.instance.pk if self.instance else None,
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
