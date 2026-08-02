"""Tests for entity subscription admin."""

from unittest.mock import MagicMock

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.entity_subscription import EntitySubscriptionAdmin
from apps.owasp.models.entity_subscription import EntitySubscription


class TestEntitySubscriptionAdmin:
    """Test EntitySubscriptionAdmin configuration."""

    def test_model_is_registered_on_default_admin_site(self):
        """Test admin package wiring registers the model."""
        assert EntitySubscription in admin.site._registry
        assert isinstance(
            admin.site._registry[EntitySubscription],
            EntitySubscriptionAdmin,
        )

    def test_admin_configuration(self):
        """Test admin configuration matches expected setup."""
        site = AdminSite()
        admin_instance = EntitySubscriptionAdmin(EntitySubscription, site)

        assert "get_entity" in admin_instance.list_display
        assert "frequency" in admin_instance.list_display
        assert "is_active" in admin_instance.list_display
        assert admin_instance.list_filter == ("frequency", "is_active", "created_at")
        assert admin_instance.search_fields == ("user__email", "user__username")
        assert admin_instance.raw_id_fields == ("user",)
        assert admin_instance.readonly_fields == ("unsubscribe_token", "created_at", "updated_at")
        assert admin_instance.autocomplete_fields == ("chapter", "committee", "project")

    def test_fieldsets_structure(self):
        """Test fieldset structure has entity fields and content toggles."""
        site = AdminSite()
        admin_instance = EntitySubscriptionAdmin(EntitySubscription, site)

        assert len(admin_instance.fieldsets) == 3

        main_fields = admin_instance.fieldsets[0][1]["fields"]
        assert "chapter" in main_fields
        assert "committee" in main_fields
        assert "project" in main_fields

        toggle_fields = admin_instance.fieldsets[1][1]["fields"]
        assert "include_issues" in toggle_fields
        assert "include_pull_requests" in toggle_fields
        assert "include_releases" in toggle_fields

        system_fieldset = admin_instance.fieldsets[2]
        assert system_fieldset[0] == "System"

    def test_get_entity_with_project(self):
        """Test get_entity returns entity name."""
        site = AdminSite()
        admin_instance = EntitySubscriptionAdmin(EntitySubscription, site)

        obj = MagicMock(spec=EntitySubscription)
        obj.entity = "OWASP ZAP"

        assert admin_instance.get_entity(obj) == "OWASP ZAP"

    def test_get_entity_without_entity(self):
        """Test get_entity returns dash when no entity."""
        site = AdminSite()
        admin_instance = EntitySubscriptionAdmin(EntitySubscription, site)

        obj = MagicMock(spec=EntitySubscription)
        obj.entity = None

        assert admin_instance.get_entity(obj) == "—"

    def test_no_inlines(self):
        """Test admin has no inlines after flattening."""
        site = AdminSite()
        admin_instance = EntitySubscriptionAdmin(EntitySubscription, site)

        assert not admin_instance.inlines
