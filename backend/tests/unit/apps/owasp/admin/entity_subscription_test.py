"""Tests for entity subscription admin."""

from unittest.mock import MagicMock, patch

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.entity_subscription import (
    ChapterPreferenceInline,
    CommitteePreferenceInline,
    EntitySubscriptionAdmin,
    ProjectPreferenceInline,
)
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

        assert len(admin_instance.fieldsets) == 2

        system_fieldset = admin_instance.fieldsets[1]
        assert system_fieldset[0] == "System"

        assert len(admin_instance.inlines) == 3


class TestPreferenceInlines:
    """Test inline admin classes for entity preferences."""

    def test_project_inline_get_queryset(self):
        """Test ProjectPreferenceInline filters by project."""
        site = AdminSite()
        inline = ProjectPreferenceInline(EntitySubscription, site)
        request = MagicMock()

        with patch.object(
            admin.StackedInline, "get_queryset", return_value=MagicMock()
        ) as mock_super_qs:
            inline.get_queryset(request)
            mock_super_qs.return_value.filter.assert_called_once_with(project__isnull=False)

    def test_chapter_inline_get_queryset(self):
        """Test ChapterPreferenceInline filters by chapter."""
        site = AdminSite()
        inline = ChapterPreferenceInline(EntitySubscription, site)
        request = MagicMock()

        with patch.object(
            admin.StackedInline, "get_queryset", return_value=MagicMock()
        ) as mock_super_qs:
            inline.get_queryset(request)
            mock_super_qs.return_value.filter.assert_called_once_with(chapter__isnull=False)

    def test_committee_inline_get_queryset(self):
        """Test CommitteePreferenceInline filters by committee."""
        site = AdminSite()
        inline = CommitteePreferenceInline(EntitySubscription, site)
        request = MagicMock()

        with patch.object(
            admin.StackedInline, "get_queryset", return_value=MagicMock()
        ) as mock_super_qs:
            inline.get_queryset(request)
            mock_super_qs.return_value.filter.assert_called_once_with(committee__isnull=False)

    def test_project_inline_configuration(self):
        """Test ProjectPreferenceInline config."""
        site = AdminSite()
        inline = ProjectPreferenceInline(EntitySubscription, site)
        assert inline.verbose_name == "Project Preference"
        assert inline.extra == 0
        assert "project" in inline.fields

    def test_chapter_inline_configuration(self):
        """Test ChapterPreferenceInline config."""
        site = AdminSite()
        inline = ChapterPreferenceInline(EntitySubscription, site)
        assert inline.verbose_name == "Chapter Preference"
        assert inline.extra == 0
        assert "chapter" in inline.fields

    def test_committee_inline_configuration(self):
        """Test CommitteePreferenceInline config."""
        site = AdminSite()
        inline = CommitteePreferenceInline(EntitySubscription, site)
        assert inline.verbose_name == "Committee Preference"
        assert inline.extra == 0
        assert "committee" in inline.fields
