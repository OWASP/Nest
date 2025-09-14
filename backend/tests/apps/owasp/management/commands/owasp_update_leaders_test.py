import io
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command

COMMAND_PATH = "apps.owasp.management.commands.owasp_update_leaders"


class TestOwaspUpdateLeaders:
    """Test suite for the owasp_update_leaders management command."""

    @pytest.fixture
    def mock_users_data(self):
        return [
            {"id": 1, "login": "john.doe", "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "login": "jane.doe", "name": "Jane Doe", "email": "jane@example.com"},
            {"id": 3, "login": "peter_jones", "name": "Peter Jones", "email": "peter@example.com"},
            {"id": 4, "login": "a", "name": "B", "email": "a@example.com"},
        ]

    def _create_mock_entity_member(self, pk, member_name, member_email="", member_id=None):
        mock_member = MagicMock()
        mock_member.pk = pk
        mock_member.member_name = member_name
        mock_member.member_email = member_email
        mock_member.member_id = member_id
        mock_member.save = MagicMock()
        return mock_member

    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.Chapter")
    @patch(f"{COMMAND_PATH}.User")
    def test_command_updates_members_with_correct_matches(
        self,
        mock_user,
        mock_chapter,
        mock_ct,
        mock_em,
        mock_users_data,
    ):
        active_users = [u for u in mock_users_data if u["id"] != 4]
        mock_user.objects.values.return_value = active_users

        mock_chapter.__name__ = "Chapter"
        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        # Mock EntityMember records that need matching
        mock_members = [
            self._create_mock_entity_member(1, "jane.doe", "jane@example.com"),
            self._create_mock_entity_member(2, "john.doe", "john@example.com"),
            self._create_mock_entity_member(3, "peter_jones", "peter@example.com"),
        ]

        # Create a proper mock queryset
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 3
        mock_queryset.__iter__ = lambda self: iter(mock_members)  # noqa: ARG005
        mock_queryset.select_related.return_value = mock_queryset
        mock_em.objects.filter.return_value = mock_queryset

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        # Verify EntityMember filter was called correctly
        mock_em.objects.filter.assert_called_once()
        filter_call = mock_em.objects.filter.call_args
        assert filter_call[1]["entity_type"] == mock_ct.objects.get_for_model.return_value
        assert filter_call[1]["role"] == mock_em.Role.LEADER
        assert filter_call[1]["member__isnull"] is True

        # Verify all members were matched and saved
        assert mock_members[0].save.called
        assert mock_members[1].save.called
        assert mock_members[2].save.called

        # Verify correct member_id assignments
        assert mock_members[0].member_id == 2  # jane.doe
        assert mock_members[1].member_id == 1  # john.doe
        assert mock_members[2].member_id == 3  # peter_jones

        assert "Matched 3 out of 3 Chapter leaders" in out.getvalue()

    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.Chapter")
    @patch(f"{COMMAND_PATH}.User")
    def test_fuzzy_match_below_threshold(
        self, mock_user, mock_chapter, mock_ct, mock_em, mock_users_data
    ):
        mock_user.objects.values.return_value = mock_users_data
        mock_chapter.__name__ = "Chapter"
        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        # Mock EntityMember with name that won't match above threshold
        mock_members = [
            self._create_mock_entity_member(1, "Jone Doe", "jone@example.com"),
        ]

        # Create a proper mock queryset
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda self: iter(mock_members)  # noqa: ARG005
        mock_queryset.select_related.return_value = mock_queryset
        mock_em.objects.filter.return_value = mock_queryset

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", "--threshold=95", stdout=out)

        # Verify no matches were made
        assert not mock_members[0].save.called
        assert "No match found for 'Jone Doe'" in out.getvalue()
        assert "1 leaders remain unmatched" in out.getvalue()

    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.User")
    @patch(f"{COMMAND_PATH}.Chapter")
    def test_no_unmatched_members_found(
        self, mock_chapter, mock_user, mock_ct, mock_em, mock_users_data
    ):
        mock_user.objects.values.return_value = mock_users_data
        mock_chapter.__name__ = "Chapter"
        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        # Mock empty EntityMember queryset
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_queryset.__iter__ = lambda self: iter([])  # noqa: ARG005
        mock_queryset.select_related.return_value = mock_queryset
        mock_em.objects.filter.return_value = mock_queryset

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        assert "No unmatched Chapter leaders found." in out.getvalue()

    @patch(f"{COMMAND_PATH}.fuzz")
    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.User")
    @patch(f"{COMMAND_PATH}.Chapter")
    def test_exact_match_is_preferred_over_fuzzy(
        self, mock_chapter, mock_user, mock_ct, mock_em, mock_fuzz, mock_users_data
    ):
        mock_user.objects.values.return_value = mock_users_data
        mock_chapter.__name__ = "Chapter"
        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        # Mock EntityMember with exact match
        mock_members = [
            self._create_mock_entity_member(1, "john.doe", "john@example.com"),
        ]

        # Create a proper mock queryset
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda self: iter(mock_members)  # noqa: ARG005
        mock_queryset.select_related.return_value = mock_queryset
        mock_em.objects.filter.return_value = mock_queryset

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        # Verify exact match was used (fuzzy matching should not be called)
        mock_fuzz.token_sort_ratio.assert_not_called()

        # Verify member was matched and saved
        assert mock_members[0].save.called
        assert mock_members[0].member_id == 1  # john.doe
        assert "Matched 1 out of 1 Chapter leaders" in out.getvalue()
