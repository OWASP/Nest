from unittest.mock import patch

from django.contrib.admin import ModelAdmin

from apps.owasp.admin.mixins import (
    BaseOwaspAdminMixin,
    EntityChannelInline,
    GenericEntityAdminMixin,
    StandardOwaspAdminMixin,
)
from apps.owasp.models.project import Project


class TestBaseOwaspAdminMixin:
    """Tests for BaseOwaspAdminMixin."""

    class MockAdmin(BaseOwaspAdminMixin, ModelAdmin):
        """Mock admin class for testing BaseOwaspAdminMixin."""

        model = Project

    def test_get_base_list_display(self, mocker):
        admin = self.MockAdmin(Project, mocker.Mock())
        display = admin.get_base_list_display("extra_field")

        assert "extra_field" in display
        assert "created_at" in display
        assert "updated_at" in display
        assert "name" in display

    def test_get_base_search_fields(self, mocker):
        admin = self.MockAdmin(Project, mocker.Mock())
        fields = admin.get_base_search_fields("extra_search")

        assert "name" in fields
        assert "key" in fields
        assert "extra_search" in fields


class TestGenericEntityAdminMixin:
    """Tests for GenericEntityAdminMixin."""

    class MockGenericAdmin(GenericEntityAdminMixin, ModelAdmin):
        """Mock admin class for testing GenericEntityAdminMixin."""

        model = Project

    def test_custom_field_owasp_url(self, mocker):
        admin = self.MockGenericAdmin(Project, mocker.Mock())
        obj = mocker.Mock()
        obj.key = "test-project"

        url = admin.custom_field_owasp_url(obj)
        assert "href='https://owasp.org/test-project'" in url
        assert "target='_blank'" in url

    def test_custom_field_owasp_url_empty(self, mocker):
        admin = self.MockGenericAdmin(Project, mocker.Mock())
        obj = mocker.Mock()
        obj.key = None

        assert admin.custom_field_owasp_url(obj) == ""

    def test_custom_field_github_urls_repositories(self, mocker):
        admin = self.MockGenericAdmin(Project, mocker.Mock())
        obj = mocker.Mock()

        repo1 = mocker.Mock()
        repo1.owner.login = "owasp"
        repo1.key = "repo-1"

        repo2 = mocker.Mock()
        repo2.owner.login = "owasp"
        repo2.key = "repo-2"

        obj.repositories.all.return_value = [repo1, repo2]

        urls = admin.custom_field_github_urls(obj)
        assert "href='https://github.com/owasp/repo-1'" in urls
        assert "href='https://github.com/owasp/repo-2'" in urls

    def test_custom_field_github_urls_fallback(self, mocker):
        admin = self.MockGenericAdmin(Project, mocker.Mock())

        class MockObj:
            pass

        obj = MockObj()
        obj.owasp_repository = mocker.Mock()
        obj.owasp_repository.owner.login = "owasp"
        obj.owasp_repository.key = "main-repo"

        urls = admin.custom_field_github_urls(obj)
        assert "href='https://github.com/owasp/main-repo'" in urls

    def test_custom_field_github_urls_no_repository(self, mocker):
        """Test custom_field_github_urls returns empty when no repositories or owasp_repository."""
        admin = self.MockGenericAdmin(Project, mocker.Mock())

        class MockObj:
            pass

        obj = MockObj()
        obj.owasp_repository = None

        urls = admin.custom_field_github_urls(obj)
        assert urls == ""

    def test_get_queryset_prefetches_repositories(self, mocker):
        """Test get_queryset prefetches repositories."""
        admin = self.MockGenericAdmin(Project, mocker.Mock())

        mock_queryset = mocker.Mock()
        mock_queryset.prefetch_related.return_value = mock_queryset

        mocker.patch.object(ModelAdmin, "get_queryset", return_value=mock_queryset)

        result = admin.get_queryset(mocker.Mock())

        mock_queryset.prefetch_related.assert_called_once_with("repositories")
        assert result == mock_queryset

    def test_format_github_link_no_repository(self, mocker):
        """Test _format_github_link returns empty string when repository is None."""
        admin = self.MockGenericAdmin(Project, mocker.Mock())
        assert admin._format_github_link(None) == ""

    def test_format_github_link_no_owner(self, mocker):
        """Test _format_github_link returns empty string when owner is None."""
        admin = self.MockGenericAdmin(Project, mocker.Mock())
        mock_repo = mocker.Mock()
        mock_repo.owner = None
        assert admin._format_github_link(mock_repo) == ""

    def test_format_github_link_no_owner_login(self, mocker):
        """Test _format_github_link returns empty string when owner.login is None."""
        admin = self.MockGenericAdmin(Project, mocker.Mock())
        mock_repo = mocker.Mock()
        mock_repo.owner.login = None
        assert admin._format_github_link(mock_repo) == ""

    def test_format_github_link_no_key(self, mocker):
        """Test _format_github_link returns empty string when repository key is None."""
        admin = self.MockGenericAdmin(Project, mocker.Mock())
        mock_repo = mocker.Mock()
        mock_repo.owner.login = "owasp"
        mock_repo.key = None
        assert admin._format_github_link(mock_repo) == ""


class TestEntityChannelInline:
    """Tests for EntityChannelInline."""

    def test_formfield_for_dbfield_channel_id(self, mocker):
        """Test that channel_id field gets ChannelIdWidget."""
        from apps.owasp.admin.widgets import ChannelIdWidget

        inline = EntityChannelInline(Project, mocker.Mock())
        mock_db_field = mocker.Mock()
        mock_db_field.name = "channel_id"
        mock_request = mocker.Mock()
        with patch.object(
            EntityChannelInline.__bases__[0], "formfield_for_dbfield"
        ) as mock_parent:
            mock_parent.return_value = mocker.Mock()
            inline.formfield_for_dbfield(mock_db_field, mock_request)
            call_kwargs = mock_parent.call_args[1]
            assert isinstance(call_kwargs.get("widget"), ChannelIdWidget)

    @patch("apps.owasp.admin.mixins.ContentType")
    def test_formfield_for_dbfield_channel_type(self, mock_content_type, mocker):
        """Test that channel_type field gets limited queryset."""
        inline = EntityChannelInline(Project, mocker.Mock())
        mock_db_field = mocker.Mock()
        mock_db_field.name = "channel_type"
        mock_request = mocker.Mock()

        mock_conversation_ct = mocker.Mock()
        mock_conversation_ct.id = 1
        mock_content_type.objects.get_for_model.return_value = mock_conversation_ct
        mock_content_type.objects.filter.return_value = mocker.Mock()
        with patch.object(
            EntityChannelInline.__bases__[0], "formfield_for_dbfield"
        ) as mock_parent:
            mock_parent.return_value = mocker.Mock()
            inline.formfield_for_dbfield(mock_db_field, mock_request)
            mock_content_type.objects.filter.assert_called_once_with(id=mock_conversation_ct.id)
            call_kwargs = mock_parent.call_args[1]
            assert "queryset" in call_kwargs
            assert "initial" in call_kwargs

    def test_formfield_for_dbfield_other_field(self, mocker):
        """Test that other fields use default parent behavior."""
        inline = EntityChannelInline(Project, mocker.Mock())
        mock_db_field = mocker.Mock()
        mock_db_field.name = "other_field"
        mock_request = mocker.Mock()

        with patch.object(
            EntityChannelInline.__bases__[0], "formfield_for_dbfield"
        ) as mock_parent:
            mock_result = mocker.Mock()
            mock_parent.return_value = mock_result

            result = inline.formfield_for_dbfield(mock_db_field, mock_request)

            # Should call parent with unmodified kwargs
            assert result == mock_result
            mock_parent.assert_called_once()
            call_kwargs = mock_parent.call_args[1]
            # Should not have widget, queryset, or initial in kwargs for other fields
            assert "widget" not in call_kwargs or not isinstance(call_kwargs.get("widget"), type)


class TestStandardOwaspAdminMixin:
    """Tests for StandardOwaspAdminMixin."""

    class MockStandardAdmin(StandardOwaspAdminMixin, ModelAdmin):
        """Mock admin class for testing StandardOwaspAdminMixin."""

        model = Project

    def test_get_common_config_with_list_display(self, mocker):
        admin = self.MockStandardAdmin(Project, mocker.Mock())
        config = admin.get_common_config(extra_list_display=("field1", "field2"))

        assert "list_display" in config
        assert "field1" in config["list_display"]
        assert "field2" in config["list_display"]

    def test_get_common_config_with_search_fields(self, mocker):
        admin = self.MockStandardAdmin(Project, mocker.Mock())
        config = admin.get_common_config(extra_search_fields=("search1",))

        assert "search_fields" in config
        assert "search1" in config["search_fields"]

    def test_get_common_config_with_list_filters(self, mocker):
        admin = self.MockStandardAdmin(Project, mocker.Mock())
        config = admin.get_common_config(extra_list_filters=("filter1",))

        assert "list_filter" in config
        assert "filter1" in config["list_filter"]

    def test_get_common_config_empty(self, mocker):
        admin = self.MockStandardAdmin(Project, mocker.Mock())
        config = admin.get_common_config()

        assert config == {}

    def test_get_common_config_all_options(self, mocker):
        admin = self.MockStandardAdmin(Project, mocker.Mock())
        config = admin.get_common_config(
            extra_list_display=("display1",),
            extra_search_fields=("search1",),
            extra_list_filters=("filter1",),
        )

        assert "list_display" in config
        assert "search_fields" in config
        assert "list_filter" in config
