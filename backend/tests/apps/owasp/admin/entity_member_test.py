"""Tests for EntityMemberAdmin class."""

from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.entity_member import EntityMemberAdmin
from apps.owasp.models.entity_member import EntityMember


class TestEntityMemberAdmin:
    """Test cases for EntityMemberAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = EntityMemberAdmin(EntityMember, self.site)

    def test_approve_members_action(self):
        """Test the approve_members admin action."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.update.return_value = 3

        self.admin.approve_members(mock_request, mock_queryset)

        mock_queryset.update.assert_called_once_with(is_active=True, is_reviewed=True)
        mock_request.assert_not_called()

    def test_entity_display_with_entity(self):
        """Test entity display method when entity exists."""
        mock_obj = MagicMock()
        mock_obj.entity = MagicMock()
        mock_obj.entity_type = MagicMock()
        mock_obj.entity_type.app_label = "owasp"
        mock_obj.entity_type.model = "project"
        mock_obj.entity_id = 1

        with patch("apps.owasp.admin.entity_member.reverse") as mock_reverse:
            mock_reverse.return_value = "/admin/owasp/project/1/change/"
            result = self.admin.entity(mock_obj)

        assert "href" in result
        assert 'target="_blank"' in result

    def test_entity_display_without_entity(self):
        """Test entity display method when entity is None."""
        mock_obj = MagicMock()
        mock_obj.entity = None

        result = self.admin.entity(mock_obj)

        assert result == "-"

    def test_owasp_url_display_with_entity(self):
        """Test OWASP URL display when entity exists."""
        mock_obj = MagicMock()
        mock_obj.entity = MagicMock()
        mock_obj.entity.owasp_url = "https://owasp.org/www-project-test"

        result = self.admin.owasp_url(mock_obj)

        assert "href" in result
        assert "https://owasp.org/www-project-test" in result
        assert "↗️" in result

    def test_owasp_url_display_without_entity(self):
        """Test OWASP URL display when entity is None."""
        mock_obj = MagicMock()
        mock_obj.entity = None

        result = self.admin.owasp_url(mock_obj)

        assert result == "-"

    def test_get_search_results_without_search_term(self):
        """Test get_search_results without a search term."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()

        with patch.object(
            EntityMemberAdmin.__bases__[0],
            "get_search_results",
            return_value=(mock_queryset, False),
        ):
            result_qs, use_distinct = self.admin.get_search_results(
                mock_request, mock_queryset, ""
            )

        assert result_qs == mock_queryset
        assert not use_distinct

    def test_get_search_results_with_search_term(self):
        """Test get_search_results with a search term finds entities."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.__or__ = MagicMock(return_value=mock_queryset)

        with (
            patch.object(
                EntityMemberAdmin.__bases__[0],
                "get_search_results",
                return_value=(mock_queryset, False),
            ),
            patch("apps.owasp.admin.entity_member.Project") as mock_project,
            patch("apps.owasp.admin.entity_member.Chapter") as mock_chapter,
            patch("apps.owasp.admin.entity_member.Committee") as mock_committee,
            patch("apps.owasp.admin.entity_member.ContentType") as mock_ct,
        ):
            mock_project.objects.filter.return_value.values_list.return_value = [1, 2]
            mock_chapter.objects.filter.return_value.values_list.return_value = [3]
            mock_committee.objects.filter.return_value.values_list.return_value = []
            mock_ct.objects.get_for_model.return_value = MagicMock()

            self.admin.model = MagicMock()
            self.admin.model.objects.filter.return_value = MagicMock()

            _result_qs, use_distinct = self.admin.get_search_results(
                mock_request, mock_queryset, "test-project"
            )

        assert use_distinct
