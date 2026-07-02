"""Tests for BoardOfDirectorsAdmin."""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.board_of_directors import BoardOfDirectorsAdmin
from apps.owasp.models.board_of_directors import BoardOfDirectors


class TestBoardOfDirectorsAdmin:
    """Tests for BoardOfDirectorsAdmin."""

    def test_filter_horizontal(self):
        """Test filter_horizontal includes reviewers."""
        admin_instance = BoardOfDirectorsAdmin(BoardOfDirectors, AdminSite())

        assert admin_instance.filter_horizontal == ("reviewers",)

    def test_list_filter(self):
        """Test list_filter includes year."""
        admin_instance = BoardOfDirectorsAdmin(BoardOfDirectors, AdminSite())

        assert admin_instance.list_filter == ("year",)

    def test_ordering(self):
        """Test ordering is by year descending."""
        admin_instance = BoardOfDirectorsAdmin(BoardOfDirectors, AdminSite())

        assert admin_instance.ordering == ("-year",)

    def test_search_fields(self):
        """Test search_fields includes year."""
        admin_instance = BoardOfDirectorsAdmin(BoardOfDirectors, AdminSite())

        assert admin_instance.search_fields == ("year",)

    def test_is_model_admin_subclass(self):
        """Test admin inherits from ModelAdmin."""
        assert issubclass(BoardOfDirectorsAdmin, admin.ModelAdmin)
