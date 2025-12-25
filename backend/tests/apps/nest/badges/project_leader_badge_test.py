"""Tests for the OWASP Project Leader badge handler."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.nest.badges.project_leader_badge import OWASPProjectLeaderBadgeHandler
from apps.owasp.models.entity_member import EntityMember


class TestOWASPProjectLeaderBadgeHandler(SimpleTestCase):

    @patch("apps.nest.badges.project_leader_badge.User")
    @patch("apps.nest.badges.project_leader_badge.EntityMember")
    @patch("apps.nest.badges.project_leader_badge.Project")
    @patch("apps.nest.badges.project_leader_badge.ContentType")
    def test_get_eligible_users_query(
        self, 
        mock_content_type, 
        mock_project_model, 
        mock_entity_member, 
        mock_user_model
    ):
        """Test that get_eligible_users queries for active, reviewed leaders."""
        handler = OWASPProjectLeaderBadgeHandler()

        mock_ct_instance = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_ct_instance        
        mock_leaders_qs = MagicMock()
        mock_entity_member.objects.filter.return_value = mock_leaders_qs
        mock_leaders_qs.values_list.return_value = [101, 102]

        handler.get_eligible_users()

        mock_content_type.objects.get_for_model.assert_called_once_with(mock_project_model)
        mock_entity_member.objects.filter.assert_called_once_with(
            entity_type=mock_ct_instance,
            role=mock_entity_member.Role.LEADER,
            is_active=True,
            is_reviewed=True,
            member__isnull=False,
        )
        mock_user_model.objects.filter.assert_called_once_with(id__in=[101, 102])
        mock_user_model.objects.filter.return_value.distinct.assert_called_once()