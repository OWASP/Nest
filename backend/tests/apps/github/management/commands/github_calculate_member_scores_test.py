"""Tests for github_calculate_member_scores management command."""

from unittest.mock import MagicMock, patch

from apps.github.management.commands.github_calculate_member_scores import Command


class TestCalculateMemberScoresCommand:
    """Test suite for the calculate member scores command."""

    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    @patch("apps.github.management.commands.github_calculate_member_scores.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_calculate_member_scores.BATCH_SIZE", 100)
    def test_handle_all_users(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user_model,
    ):
        """Test command processes all users."""
        mock_user_1 = MagicMock(id=1, is_owasp_staff=False)
        mock_user_1.contribution_data = {}
        mock_user_2 = MagicMock(id=2, is_owasp_staff=False)
        mock_user_2.contribution_data = {}

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.iterator.return_value = [mock_user_1, mock_user_2]
        mock_qs.exists.return_value = True
        mock_user_model.objects.all.return_value = mock_qs
        mock_filter = mock_user_model.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()

        mock_rc_objects = MagicMock()
        mock_rc_objects.exclude.return_value.values.return_value.annotate.return_value = []
        mock_repository_contributor.objects = mock_rc_objects

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle(user=None)

        mock_user_model.objects.all.assert_called_once()
        mock_user_model.bulk_save.assert_called()

    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    @patch("apps.github.management.commands.github_calculate_member_scores.RepositoryContributor")
    @patch.object(Command, "_get_leadership_data", return_value={})
    @patch("apps.github.management.commands.github_calculate_member_scores.BATCH_SIZE", 100)
    def test_handle_specific_user(
        self,
        mock_leadership_data,
        mock_repository_contributor,
        mock_user_model,
    ):
        """Test command processes a specific user."""
        mock_user = MagicMock(id=1, is_owasp_staff=False)
        mock_user.contribution_data = {}

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.iterator.return_value = [mock_user]
        mock_user_model.objects.filter.return_value = mock_qs
        mock_filter = mock_user_model.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = []
        mock_filter.values_list.return_value.distinct.return_value = set()

        mock_rc_objects = MagicMock()
        mock_rc_objects.exclude.return_value.values.return_value.annotate.return_value = []
        mock_repository_contributor.objects = mock_rc_objects

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle(user="testuser")

        mock_user_model.objects.filter.assert_any_call(login="testuser")

    @patch("apps.github.management.commands.github_calculate_member_scores.User")
    def test_handle_user_not_found(self, mock_user_model):
        """Test command handles missing user gracefully."""
        mock_qs = MagicMock()
        mock_qs.exists.return_value = False
        mock_user_model.objects.filter.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.ERROR = lambda x: x

        command.handle(user="nonexistent")

        mock_user_model.bulk_save.assert_not_called()
        command.stdout.write.assert_called_once_with("Member 'nonexistent' not found")


class TestGetLeadershipDataScoresCommand:
    """Tests for _get_leadership_data static method in calculate scores command."""

    @patch("apps.github.management.commands.github_calculate_member_scores.EntityMember")
    @patch("apps.github.management.commands.github_calculate_member_scores.ContentType")
    @patch("apps.github.management.commands.github_calculate_member_scores.Project")
    @patch("apps.github.management.commands.github_calculate_member_scores.Chapter")
    @patch("apps.github.management.commands.github_calculate_member_scores.Committee")
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

    @patch("apps.github.management.commands.github_calculate_member_scores.EntityMember")
    @patch("apps.github.management.commands.github_calculate_member_scores.ContentType")
    @patch("apps.github.management.commands.github_calculate_member_scores.Project")
    @patch("apps.github.management.commands.github_calculate_member_scores.Chapter")
    @patch("apps.github.management.commands.github_calculate_member_scores.Committee")
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

    @patch("apps.github.management.commands.github_calculate_member_scores.EntityMember")
    @patch("apps.github.management.commands.github_calculate_member_scores.ContentType")
    @patch("apps.github.management.commands.github_calculate_member_scores.Project")
    @patch("apps.github.management.commands.github_calculate_member_scores.Chapter")
    @patch("apps.github.management.commands.github_calculate_member_scores.Committee")
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

    @patch("apps.github.management.commands.github_calculate_member_scores.EntityMember")
    @patch("apps.github.management.commands.github_calculate_member_scores.ContentType")
    @patch("apps.github.management.commands.github_calculate_member_scores.Project")
    @patch("apps.github.management.commands.github_calculate_member_scores.Chapter")
    @patch("apps.github.management.commands.github_calculate_member_scores.Committee")
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

        assert "chapter_leader" not in result.get(40, {})
