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
            {"id": 1, "login": "john.doe", "name": "John Doe"},
            {"id": 2, "login": "jane.doe", "name": "Jane Doe"},
            {"id": 3, "login": "peter_jones", "name": "Peter Jones"},
            {"id": 4, "login": "a", "name": "B"},
        ]

    def _create_mock_entity(self, pk, name, leaders_raw):
        mock_entity = MagicMock()
        mock_entity.pk = pk
        mock_entity.leaders_raw = leaders_raw
        mock_entity.__str__.return_value = name
        return mock_entity

    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.Chapter")
    @patch(f"{COMMAND_PATH}.User")
    def test_command_creates_members_with_correct_order(
        self,
        mock_user,
        mock_chapter,
        mock_ct,
        mock_em,
        mock_users_data,
    ):
        active_users = [u for u in mock_users_data if u["id"] != 4]
        mock_user.objects.values.return_value = active_users

        mock_chapter.objects.all.return_value = [
            self._create_mock_entity(1, "Ordered Chapter", ["jane.doe", "john.doe", "peter_jones"])
        ]
        mock_chapter.__name__ = "Chapter"

        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        def bulk_create_side_effect(instances, *_, **__):
            return instances

        mock_em.objects.bulk_create.side_effect = bulk_create_side_effect

        def entity_member_constructor(*_, **kwargs):
            instance = MagicMock()
            instance.member_id = kwargs.get("member_id")
            instance.order = kwargs.get("order")
            return instance

        mock_em.side_effect = entity_member_constructor

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        mock_em.objects.bulk_create.assert_called_once()
        created_members = mock_em.objects.bulk_create.call_args[0][0]

        assert len(created_members) == 3

        jane = next(m for m in created_members if m.member_id == 2)
        assert jane.order == 10

        john = next(m for m in created_members if m.member_id == 1)
        assert john.order == 20

        peter = next(m for m in created_members if m.member_id == 3)
        assert peter.order == 30

    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.Chapter")
    @patch(f"{COMMAND_PATH}.User")
    def test_fuzzy_match_below_threshold(
        self, mock_user, mock_chapter, mock_ct, mock_em, mock_users_data
    ):
        mock_user.objects.values.return_value = mock_users_data
        mock_chapter.objects.all.return_value = [
            self._create_mock_entity(1, "Fuzzy Chapter", ["Jone Doe"])
        ]
        mock_chapter.__name__ = "Chapter"
        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", "--threshold=95", stdout=out)

        mock_em.objects.bulk_create.assert_not_called()
        assert "No new leader records to create" in out.getvalue()

    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.User")
    @patch(f"{COMMAND_PATH}.Chapter")
    def test_is_valid_user_filtering(
        self, mock_chapter, mock_user, mock_ct, mock_em, mock_users_data
    ):
        mock_user.objects.values.return_value = mock_users_data
        mock_chapter.objects.all.return_value = [
            self._create_mock_entity(99, "Invalid Chapter", ["a"])
        ]
        mock_chapter.__name__ = "Chapter"

        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        mock_em.objects.bulk_create.assert_not_called()
        assert "No new leader records to create" in out.getvalue()

    @patch(f"{COMMAND_PATH}.fuzz")
    @patch(f"{COMMAND_PATH}.EntityMember")
    @patch(f"{COMMAND_PATH}.ContentType")
    @patch(f"{COMMAND_PATH}.User")
    @patch(f"{COMMAND_PATH}.Chapter")
    def test_exact_match_is_preferred_over_fuzzy(
        self, mock_chapter, mock_user, mock_ct, mock_em, mock_fuzz, mock_users_data
    ):
        mock_user.objects.values.return_value = mock_users_data
        mock_chapter.objects.all.return_value = [
            self._create_mock_entity(1, "Exact Chapter", ["john.doe"])
        ]
        mock_chapter.__name__ = "Chapter"
        mock_ct.objects.get_for_model.return_value = MagicMock(spec=ContentType)

        def bulk_create_side_effect(instances, *_, **__):
            return instances

        mock_em.objects.bulk_create.side_effect = bulk_create_side_effect

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        mock_fuzz.token_sort_ratio.assert_not_called()

        assert "Created 1 new leader records" in out.getvalue()
