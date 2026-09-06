from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.e2e.management.commands.e2e_seed_users import E2E_USERS, Command


class TestE2ESeedUsersCommand:
    def test_metadata(self):
        assert Command.help == "Seed e2e test users."
        assert E2E_USERS == (
            ("e2e-mentee", "mentee"),
            ("e2e-mentor", "mentor"),
            ("e2e-user", ""),
        )

    def test_requires_e2e_environment(self):
        with (
            patch(
                "apps.e2e.management.commands.e2e_seed_users.settings.IS_E2E_ENVIRONMENT",
                new=False,
            ),
            pytest.raises(CommandError, match="e2e environment"),
        ):
            call_command(Command())

    @patch("apps.e2e.management.commands.e2e_seed_users.index.disable_indexing")
    @patch("apps.e2e.management.commands.e2e_seed_users.ContentType")
    @patch("apps.e2e.management.commands.e2e_seed_users.EntityMember")
    @patch("apps.e2e.management.commands.e2e_seed_users.Project")
    @patch("apps.e2e.management.commands.e2e_seed_users.Mentee")
    @patch("apps.e2e.management.commands.e2e_seed_users.Mentor")
    @patch("apps.e2e.management.commands.e2e_seed_users.NestUser")
    @patch("apps.e2e.management.commands.e2e_seed_users.GithubUser")
    def test_creates_users(
        self,
        mock_github_user,
        mock_nest_user,
        mock_mentor,
        mock_mentee,
        mock_project,
        mock_entity_member,
        mock_content_type,
        mock_disable_indexing,
    ):
        github_user = MagicMock()
        github_user.id = 10
        nest_user = MagicMock()
        nest_user.github_user_id = 10
        project = MagicMock(id=1)
        membership = MagicMock()
        mock_github_user.objects.get_or_create.return_value = (github_user, True)
        mock_nest_user.objects.get_or_create.return_value = (nest_user, True)
        mock_project.objects.get_or_create.return_value = (project, True)
        mock_entity_member.objects.get_or_create.return_value = (membership, True)

        with patch(
            "apps.e2e.management.commands.e2e_seed_users.settings.IS_E2E_ENVIRONMENT",
            new=True,
        ):
            call_command(Command())

        mock_disable_indexing.assert_called_once()
        assert mock_github_user.objects.get_or_create.call_count == 3
        assert mock_nest_user.objects.get_or_create.call_count == 3
        mock_mentor.objects.get_or_create.assert_called_once_with(
            github_user=github_user,
            defaults={"nest_user": nest_user},
        )
        mock_mentee.objects.get_or_create.assert_called_once_with(
            github_user=github_user,
            defaults={"nest_user": nest_user},
        )
        mock_project.objects.get_or_create.assert_called_once_with(
            key="www-project-e2e",
            defaults={"name": "E2E Project"},
        )
        mock_entity_member.objects.get_or_create.assert_called_once_with(
            entity_id=project.id,
            entity_type=mock_content_type.objects.get_for_model.return_value,
            member_name="e2e-user",
            role=mock_entity_member.Role.LEADER,
            defaults={
                "is_active": True,
                "is_reviewed": True,
                "member": github_user,
            },
        )
        membership.save.assert_called_once_with(
            update_fields=["is_active", "is_reviewed", "member"]
        )
