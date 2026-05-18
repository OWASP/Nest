"""Tests for entity leadership utilities."""

from unittest.mock import MagicMock, patch

from apps.github.models.user import User as GithubUser
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project
from apps.owasp.utils.entity_leader import user_is_entity_leader, user_is_project_leader


class TestUserIsEntityLeader:
    """Tests for user_is_entity_leader and user_is_project_leader."""

    @patch("apps.owasp.utils.entity_leader.ContentType.objects.get_for_model")
    @patch("apps.owasp.utils.entity_leader.EntityMember.objects.filter")
    def test_user_is_project_leader_true(self, mock_filter, mock_get_for_model):
        """Return True when an active, reviewed project leader membership exists."""
        github_user = MagicMock(spec=GithubUser)
        mock_filter.return_value.exists.return_value = True

        assert user_is_project_leader(github_user)

        mock_get_for_model.assert_called_once_with(Project)
        mock_filter.assert_called_once_with(
            member=github_user,
            entity_type=mock_get_for_model.return_value,
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )

    @patch("apps.owasp.utils.entity_leader.ContentType.objects.get_for_model")
    @patch("apps.owasp.utils.entity_leader.EntityMember.objects.filter")
    def test_user_is_project_leader_false(self, mock_filter, mock_get_for_model):
        """Return False when no matching project leader membership exists."""
        github_user = MagicMock(spec=GithubUser)
        mock_filter.return_value.exists.return_value = False

        assert not user_is_project_leader(github_user)

    @patch("apps.owasp.utils.entity_leader.ContentType.objects.get_for_model")
    @patch("apps.owasp.utils.entity_leader.EntityMember.objects.filter")
    def test_user_is_entity_leader_uses_entity_model(self, mock_filter, mock_get_for_model):
        """Entity model is passed through to the ContentType lookup."""
        github_user = MagicMock(spec=GithubUser)
        entity_model = MagicMock()
        mock_filter.return_value.exists.return_value = False

        user_is_entity_leader(github_user, entity_model)

        mock_get_for_model.assert_called_once_with(entity_model)
