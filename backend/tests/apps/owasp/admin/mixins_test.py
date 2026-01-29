from django.contrib.admin import ModelAdmin

from apps.owasp.admin.mixins import (
    BaseOwaspAdminMixin,
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
