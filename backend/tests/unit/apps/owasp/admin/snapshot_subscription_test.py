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

        # Check fieldsets structure
        assert len(admin.fieldsets) == 3

        # Check Content Preferences fieldset
        preferences_fieldset = admin.fieldsets[1]
        assert preferences_fieldset[0] == "Content Preferences"

        preferences_fields = preferences_fieldset[1]["fields"]
        assert "include_chapters" in preferences_fields
        assert "include_events" in preferences_fields
        assert "include_issues" in preferences_fields
        assert "include_posts" in preferences_fields
        assert "include_projects" in preferences_fields
        assert "include_pull_requests" in preferences_fields
        assert "include_releases" in preferences_fields
        assert "include_users" in preferences_fields
