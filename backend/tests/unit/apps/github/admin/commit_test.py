import pytest
from django.contrib.admin.sites import AdminSite

from apps.github.admin.commit import CommitAdmin
from apps.github.models.commit import Commit


@pytest.fixture
def commit_admin_instance():
    return CommitAdmin(model=Commit, admin_site=AdminSite())


class TestCommitAdmin:
    def test_list_display_contains_required_fields(self, commit_admin_instance):
        admin_list_display = commit_admin_instance.list_display

        assert "sha" in admin_list_display
        assert "repository" in admin_list_display
        assert "author" in admin_list_display
        assert "created_at" in admin_list_display

    def test_autocomplete_fields_configured(self, commit_admin_instance):
        autocomplete_fields = commit_admin_instance.autocomplete_fields

        assert "author" in autocomplete_fields
        assert "committer" in autocomplete_fields
        assert "repository" in autocomplete_fields

    def test_search_fields_configured(self, commit_admin_instance):
        search_fields = commit_admin_instance.search_fields

        assert "sha" in search_fields
        assert "message" in search_fields
        assert "node_id" in search_fields
        assert "repository__name" in search_fields
        assert "author__login" in search_fields

    def test_list_filter_configured(self, commit_admin_instance):
        list_filter = commit_admin_instance.list_filter

        assert "created_at" in list_filter
