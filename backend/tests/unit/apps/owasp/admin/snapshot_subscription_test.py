"""Tests for snapshot subscription admin."""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.snapshot_subscription import SnapshotSubscriptionAdmin
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class TestSnapshotSubscriptionAdmin:
    """Test SnapshotSubscriptionAdmin configuration."""

    def test_model_is_registered_on_default_admin_site(self):
        """Test admin package wiring registers the model."""
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
            "name",
            "frequency",
            "is_active",
            "created_at",
            "updated_at",
        )
        assert admin_instance.list_filter == ("frequency", "is_active", "created_at")
        assert admin_instance.search_fields == ("user__email", "user__username", "name")
        assert admin_instance.raw_id_fields == ("user",)
        assert admin_instance.readonly_fields == ("unsubscribe_token", "created_at", "updated_at")
        assert admin_instance.autocomplete_fields == (
            "subscribed_projects",
            "subscribed_chapters",
            "subscribed_committees",
        )
        assert len(admin_instance.fieldsets) == 4

        main_fieldset = admin_instance.fieldsets[0]
        assert "name" in main_fieldset[1]["fields"]

        content_fieldset = admin_instance.fieldsets[1]
        assert content_fieldset[0] == "Content Toggles"
        assert content_fieldset[1]["fields"] == (
            "include_chapters",
            "include_events",
            "include_issues",
            "include_posts",
            "include_projects",
            "include_pull_requests",
            "include_releases",
            "include_users",
        )

        entity_fieldset = admin_instance.fieldsets[2]
        assert entity_fieldset[0] == "Subscribed Entities"
        assert entity_fieldset[1]["fields"] == (
            "subscribed_projects",
            "subscribed_chapters",
            "subscribed_committees",
        )

        system_fieldset = admin_instance.fieldsets[3]
        assert system_fieldset[0] == "System"
