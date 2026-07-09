"""Tests for snapshot subscription admin."""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.snapshot_subscription import SnapshotSubscriptionAdmin
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class TestSnapshotSubscriptionAdmin:
    """Test SnapshotSubscriptionAdmin configuration."""

    def test_model_is_registered_on_default_admin_site(self):
        """Test admin package wiring registers SnapshotSubscription."""
        assert SnapshotSubscription in admin.site._registry
        assert isinstance(
            admin.site._registry[SnapshotSubscription],
            SnapshotSubscriptionAdmin,
        )

    def test_admin_configuration(self):
        """Test admin configuration matches expected setup."""
        site = AdminSite()
        admin_instance = SnapshotSubscriptionAdmin(SnapshotSubscription, site)

        assert admin_instance.list_display == (
            "user",
            "frequency",
            "is_active",
            "created_at",
            "updated_at",
        )
        assert admin_instance.list_filter == ("frequency", "is_active", "created_at")
        assert admin_instance.search_fields == ("user__email", "user__username")
        assert admin_instance.raw_id_fields == ("user",)
        assert admin_instance.readonly_fields == ("unsubscribe_token", "created_at", "updated_at")
        assert admin_instance.autocomplete_fields == ("chapters",)

        # Check fieldsets structure
        assert len(admin_instance.fieldsets) == 4

        # Check System fieldset
        system_fieldset = admin_instance.fieldsets[1]
        assert system_fieldset[0] == "System"

        # Check General Subscriptions fieldset
        preferences_fieldset = admin_instance.fieldsets[2]
        assert preferences_fieldset[0] == "General Subscriptions"
        assert preferences_fieldset[1]["fields"] == (
            "include_chapters",
            "include_events",
            "include_posts",
            "include_users",
        )

        # Check Chapter Subscriptions fieldset
        chapter_fieldset = admin_instance.fieldsets[3]
        assert chapter_fieldset[0] == "Chapter Subscriptions"
        assert chapter_fieldset[1]["fields"] == ("chapters",)
