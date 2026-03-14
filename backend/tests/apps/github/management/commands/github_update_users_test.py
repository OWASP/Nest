"""Tests for the github_update_users Django management command."""

from unittest.mock import MagicMock, patch

from django.core.management.base import BaseCommand

from apps.github.management.commands.github_update_users import Command

PROJECT_LEADER = "leader"
CHAPTER_LEADER = "leader"
COMMITTEE_MEMBER = "member"


class TestGithubUpdateUsersCommand:
    def test_command_help_text(self):
        """Test that the command has the correct help text."""
        command = Command()
        assert command.help == "Update GitHub users."

    def test_command_inheritance(self):
        """Test that the command inherits from BaseCommand."""
        command = Command()

        assert isinstance(command, BaseCommand)

    def test_add_arguments(self):
        """Test that the command adds the correct arguments."""
        command = Command()
        parser = MagicMock()

        command.add_arguments(parser)

        parser.add_argument.assert_called_once_with(
            "--offset", default=0, required=False, type=int
        )

    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_default_offset(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user,
    ):
        """Test command execution with default offset."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user3 = MagicMock(id=3, title="User 3", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}
        mock_user3.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 3
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2, mock_user3]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()
        mock_user.get_non_indexable_logins.return_value = []

        mock_rc_objects = MagicMock()
        mock_rc_objects.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 1, "total_contributions": 10, "repo_count": 2},
            {"user_id": 2, "total_contributions": 20, "repo_count": 3},
            {"user_id": 3, "total_contributions": 30, "repo_count": 4},
        ]
        mock_repository_contributor.objects = mock_rc_objects

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        mock_user.objects.order_by.assert_called_once_with("-created_at")
        mock_users_queryset.count.assert_called_once()
        mock_users_queryset.__getitem__.assert_called_once_with(slice(0, None))

        assert mock_rc_objects.exclude.return_value.values.call_count == 1
        assert mock_rc_objects.exclude.return_value.values.return_value.annotate.call_count == 1

        assert mock_user1.contributions_count == 10
        assert mock_user2.contributions_count == 20
        assert mock_user3.contributions_count == 30

        assert mock_user.bulk_save.call_count == 2
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1, mock_user2]
        assert mock_user.bulk_save.call_args_list[1][0][0] == [mock_user3]

    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_custom_offset(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user,
    ):
        """Test command execution with custom offset."""
        mock_user1 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=3, title="User 3", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 3
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()
        mock_user.get_non_indexable_logins.return_value = []

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 2, "total_contributions": 20, "repo_count": 2},
            {"user_id": 3, "total_contributions": 30, "repo_count": 3},
        ]
        mock_repository_contributor.objects = mock_rc_queryset

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=1)

        mock_users_queryset.__getitem__.assert_called_once_with(slice(1, None))

        assert mock_user1.contributions_count == 20
        assert mock_user2.contributions_count == 30

        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1, mock_user2]

    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 3)
    def test_handle_with_users_having_no_contributions(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user,
    ):
        """Test command execution when users have no contributions."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 2
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()
        mock_user.get_non_indexable_logins.return_value = []

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = []
        mock_repository_contributor.objects = mock_rc_queryset

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user1.contributions_count == 0
        assert mock_user2.contributions_count == 0

    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 1)
    def test_handle_with_single_user(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user,
    ):
        """Test command execution with single user."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 1
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()
        mock_user.get_non_indexable_logins.return_value = []

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 1, "total_contributions": 15, "repo_count": 2},
        ]
        mock_repository_contributor.objects = mock_rc_queryset

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user1.contributions_count == 15
        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1]

    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_empty_user_list(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user,
    ):
        """Test command execution with no users."""
        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 0
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = []
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()
        mock_user.get_non_indexable_logins.return_value = []

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = []
        mock_repository_contributor.objects = mock_rc_queryset

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user.bulk_save.call_count == 0

    @patch("apps.github.management.commands.github_update_users.User")
    @patch("apps.github.management.commands.github_update_users.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_update_users.BATCH_SIZE", 2)
    def test_handle_with_exact_batch_size(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user,
    ):
        """Test command execution when user count equals batch size."""
        mock_user1 = MagicMock(id=1, title="User 1", contributions_count=0, is_owasp_staff=False)
        mock_user2 = MagicMock(id=2, title="User 2", contributions_count=0, is_owasp_staff=False)
        mock_user1.contribution_data = {}
        mock_user2.contribution_data = {}

        mock_users_queryset = MagicMock()
        mock_users_queryset.count.return_value = 2
        mock_sliced_qs = MagicMock()
        mock_sliced_qs.iterator.return_value = [mock_user1, mock_user2]
        mock_users_queryset.__getitem__.return_value = mock_sliced_qs

        mock_user.objects.order_by.return_value = mock_users_queryset
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()
        mock_user.get_non_indexable_logins.return_value = []

        mock_rc_queryset = MagicMock()
        mock_rc_queryset.exclude.return_value.values.return_value.annotate.return_value = [
            {"user_id": 1, "total_contributions": 10, "repo_count": 2},
            {"user_id": 2, "total_contributions": 20, "repo_count": 3},
        ]
        mock_repository_contributor.objects = mock_rc_queryset

        command = Command()
        command.stdout = MagicMock()
        command.handle(offset=0)

        assert mock_user1.contributions_count == 10
        assert mock_user2.contributions_count == 20
        assert mock_user.bulk_save.call_count == 1
        assert mock_user.bulk_save.call_args_list[0][0][0] == [mock_user1, mock_user2]


class TestGetLeadershipData:
    """Tests for _get_leadership_data static method."""

    @patch("apps.github.management.commands.github_update_users.EntityMember")
    @patch("apps.github.management.commands.github_update_users.ContentType")
    @patch("apps.github.management.commands.github_update_users.Project")
    @patch("apps.github.management.commands.github_update_users.Chapter")
    @patch("apps.github.management.commands.github_update_users.Committee")
    def test_project_leader_counted(
        self,
        mock_committee,
        mock_chapter,
        mock_project,
        mock_content_type,
        mock_entity_member,
    ):
        """Test that project leader roles are counted correctly."""
        mock_content_type.objects.get_for_model.side_effect = lambda model: MagicMock(
            id={"Project": 1, "Chapter": 2, "Committee": 3}[model.__name__]
        )
        mock_project.__name__ = "Project"
        mock_chapter.__name__ = "Chapter"
        mock_committee.__name__ = "Committee"

        mock_entity_member.Role.LEADER = "leader"
        mock_entity_member.Role.MEMBER = "member"
        mock_em_qs = mock_entity_member.objects.filter.return_value
        mock_em_qs.values.return_value.annotate.return_value = [
            {"member_id": 10, "entity_type_id": 1, "role": "leader", "count": 2},
        ]

        result = Command._get_leadership_data()

        assert result[10]["project_leader"] == 2
        assert "chapter_leader" not in result.get(10, {})

    @patch("apps.github.management.commands.github_update_users.EntityMember")
    @patch("apps.github.management.commands.github_update_users.ContentType")
    @patch("apps.github.management.commands.github_update_users.Project")
    @patch("apps.github.management.commands.github_update_users.Chapter")
    @patch("apps.github.management.commands.github_update_users.Committee")
    def test_chapter_leader_counted(
        self,
        mock_committee,
        mock_chapter,
        mock_project,
        mock_content_type,
        mock_entity_member,
    ):
        """Test that chapter leader roles are counted correctly."""
        mock_content_type.objects.get_for_model.side_effect = lambda model: MagicMock(
            id={"Project": 1, "Chapter": 2, "Committee": 3}[model.__name__]
        )
        mock_project.__name__ = "Project"
        mock_chapter.__name__ = "Chapter"
        mock_committee.__name__ = "Committee"

        mock_entity_member.Role.LEADER = "leader"
        mock_entity_member.Role.MEMBER = "member"
        mock_em_qs = mock_entity_member.objects.filter.return_value
        mock_em_qs.values.return_value.annotate.return_value = [
            {"member_id": 20, "entity_type_id": 2, "role": "leader", "count": 3},
        ]

        result = Command._get_leadership_data()

        assert result[20]["chapter_leader"] == 3
        assert "project_leader" not in result.get(20, {})

    @patch("apps.github.management.commands.github_update_users.EntityMember")
    @patch("apps.github.management.commands.github_update_users.ContentType")
    @patch("apps.github.management.commands.github_update_users.Project")
    @patch("apps.github.management.commands.github_update_users.Chapter")
    @patch("apps.github.management.commands.github_update_users.Committee")
    def test_committee_member_counted(
        self,
        mock_committee,
        mock_chapter,
        mock_project,
        mock_content_type,
        mock_entity_member,
    ):
        """Test that committee member roles are counted correctly."""
        mock_content_type.objects.get_for_model.side_effect = lambda model: MagicMock(
            id={"Project": 1, "Chapter": 2, "Committee": 3}[model.__name__]
        )
        mock_project.__name__ = "Project"
        mock_chapter.__name__ = "Chapter"
        mock_committee.__name__ = "Committee"

        mock_entity_member.Role.LEADER = "leader"
        mock_entity_member.Role.MEMBER = "member"
        mock_em_qs = mock_entity_member.objects.filter.return_value
        mock_em_qs.values.return_value.annotate.return_value = [
            {"member_id": 30, "entity_type_id": 3, "role": "member", "count": 1},
        ]

        result = Command._get_leadership_data()

        assert result[30]["committee_member"] == 1

    @patch("apps.github.management.commands.github_update_users.EntityMember")
    @patch("apps.github.management.commands.github_update_users.ContentType")
    @patch("apps.github.management.commands.github_update_users.Project")
    @patch("apps.github.management.commands.github_update_users.Chapter")
    @patch("apps.github.management.commands.github_update_users.Committee")
    def test_chapter_member_role_not_counted_as_leader(
        self,
        mock_committee,
        mock_chapter,
        mock_project,
        mock_content_type,
        mock_entity_member,
    ):
        """Test that regular MEMBER role in chapter is NOT counted as chapter leader."""
        mock_content_type.objects.get_for_model.side_effect = lambda model: MagicMock(
            id={"Project": 1, "Chapter": 2, "Committee": 3}[model.__name__]
        )
        mock_project.__name__ = "Project"
        mock_chapter.__name__ = "Chapter"
        mock_committee.__name__ = "Committee"

        mock_entity_member.Role.LEADER = "leader"
        mock_entity_member.Role.MEMBER = "member"
        mock_em_qs = mock_entity_member.objects.filter.return_value
        mock_em_qs.values.return_value.annotate.return_value = [
            {"member_id": 40, "entity_type_id": 2, "role": "member", "count": 5},
        ]

        result = Command._get_leadership_data()

        # Regular chapter member should NOT get chapter_leader credit
        assert "chapter_leader" not in result.get(40, {})

    @patch("apps.github.management.commands.github_update_users.EntityMember")
    @patch("apps.github.management.commands.github_update_users.ContentType")
    @patch("apps.github.management.commands.github_update_users.Project")
    @patch("apps.github.management.commands.github_update_users.Chapter")
    @patch("apps.github.management.commands.github_update_users.Committee")
    def test_empty_memberships(
        self,
        mock_committee,
        mock_chapter,
        mock_project,
        mock_content_type,
        mock_entity_member,
    ):
        """Test that empty memberships returns empty dict."""
        mock_content_type.objects.get_for_model.return_value = MagicMock(id=1)
        mock_entity_member.Role.LEADER = "leader"
        mock_entity_member.Role.MEMBER = "member"
        mock_em_qs = mock_entity_member.objects.filter.return_value
        mock_em_qs.values.return_value.annotate.return_value = []

        result = Command._get_leadership_data()

        assert result == {}
