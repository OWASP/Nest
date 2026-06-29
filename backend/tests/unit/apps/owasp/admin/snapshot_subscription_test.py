"""Tests for snapshot subscription admin."""

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.snapshot_subscription import SnapshotSubscriptionAdmin
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class TestSnapshotSubscriptionAdmin:
    """Test SnapshotSubscriptionAdmin configuration."""

    def test_admin_configuration(self):
        """Test admin configuration matches expected setup."""
        site = AdminSite()
        admin = SnapshotSubscriptionAdmin(SnapshotSubscription, site)

        assert admin.list_display == (
            "user",
            "frequency",
            "is_active",
            "created_at",
            "updated_at",
        )
        assert admin.list_filter == ("frequency", "is_active", "created_at")
        assert admin.search_fields == ("user__email", "user__username")
        assert admin.raw_id_fields == ("user",)
        assert admin.readonly_fields == ("unsubscribe_token", "created_at", "updated_at")
        assert admin.autocomplete_fields == ("subscribed_projects", "subscribed_chapters")

        # Check fieldsets structure
        assert len(admin.fieldsets) == 4

        # Check Content Preferences fieldset
        preferences_fieldset = admin.fieldsets[1]
        assert preferences_fieldset[0] == "Content Preferences"

        assert preferences_fieldset[1]["fields"] == (
            "include_chapters",
            "include_events",
            "include_issues",
            "include_posts",
            "include_projects",
            "include_pull_requests",
            "include_releases",
            "include_users",
        )

        # Check Subscription Filters fieldset
        filters_fieldset = admin.fieldsets[2]
        assert filters_fieldset[0] == "Subscription Filters"
        assert filters_fieldset[1]["fields"] == (
            "subscribed_projects",
            "subscribed_chapters",
        )
