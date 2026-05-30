"""Tests for User.is_project_leader."""

from unittest.mock import patch

from apps.github.models.user import User
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


class TestUserIsProjectLeader:
    """Tests for is_project_leader."""

    @patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    @patch("apps.owasp.models.entity_member.EntityMember.objects.filter")
    def test_is_project_leader_true(self, mock_filter, mock_get_for_model):
        """Return True when an active, reviewed project leader membership exists."""
        user = User(id=1, login="testuser", node_id="U_test123")
        mock_filter.return_value.exists.return_value = True

        assert user.is_project_leader

        mock_get_for_model.assert_called_once_with(Project)
        mock_filter.assert_called_once_with(
            entity_type=mock_get_for_model.return_value,
            is_active=True,
            is_reviewed=True,
            member=user,
            role=EntityMember.Role.LEADER,
        )

    @patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    @patch("apps.owasp.models.entity_member.EntityMember.objects.filter")
    def test_is_project_leader_false(self, mock_filter, mock_get_for_model):
        """Return False when no matching project leader membership exists."""
        user = User(id=1, login="testuser", node_id="U_test123")
        mock_filter.return_value.exists.return_value = False

        assert not user.is_project_leader
