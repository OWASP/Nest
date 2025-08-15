import io
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

COMMAND_PATH = "apps.owasp.management.commands.owasp_update_leaders"


class OwaspUpdateLeadersTest(SimpleTestCase):
    """Test suite for the owasp_update_leaders management command using mocks."""

    @classmethod
    def setUpClass(cls):
        """Start all necessary patchers once for the entire test class."""
        super().setUpClass()
        cls.user_patcher = patch(f"{COMMAND_PATH}.User")
        cls.chapter_patcher = patch(f"{COMMAND_PATH}.Chapter")
        cls.committee_patcher = patch(f"{COMMAND_PATH}.Committee")
        cls.project_patcher = patch(f"{COMMAND_PATH}.Project")
        cls.content_type_patcher = patch(f"{COMMAND_PATH}.ContentType")
        cls.entity_member_patcher = patch(f"{COMMAND_PATH}.EntityMember")

        cls.mock_user = cls.user_patcher.start()
        cls.mock_chapter = cls.chapter_patcher.start()
        cls.mock_committee = cls.committee_patcher.start()
        cls.mock_project = cls.project_patcher.start()
        cls.mock_content_type = cls.content_type_patcher.start()
        cls.mock_entity_member = cls.entity_member_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop all patchers after all tests have run."""
        super().tearDownClass()
        patch.stopall()

    def setUp(self):
        """Configure the behavior of the mocks before each test."""
        for mock in [
            self.mock_user,
            self.mock_chapter,
            self.mock_committee,
            self.mock_project,
            self.mock_content_type,
            self.mock_entity_member,
        ]:
            mock.reset_mock()

        self.mock_chapter.__name__ = "Chapter"
        self.mock_committee.__name__ = "Committee"
        self.mock_project.__name__ = "Project"

        def entity_member_side_effect(*_, **kwargs):
            instance = MagicMock()
            instance.entity_id = kwargs.get("entity_id")
            instance.member_id = kwargs.get("member_id")
            return instance

        self.mock_entity_member.side_effect = entity_member_side_effect

        def bulk_create_side_effect(instances, *_, **__):
            return instances

        self.mock_entity_member.objects.bulk_create.side_effect = bulk_create_side_effect

        self.mock_users_data = [
            {"id": 1, "login": "john.doe", "name": "John Doe"},
            {"id": 2, "login": "jane.doe", "name": "Jane Doe"},
            {"id": 3, "login": "peter_jones", "name": "Peter Jones"},
            {"id": 4, "login": "samantha", "name": "Samantha Smith"},
            {"id": 5, "login": "a", "name": "B"},
        ]
        self.mock_user.objects.values.return_value = self.mock_users_data

        self.mock_chapter_1 = self._create_mock_entity(
            1, "Test Chapter 1", ["john.doe", "Unknown Person"]
        )
        self.mock_chapter_2 = self._create_mock_entity(2, "Test Chapter 2", ["Jane Doe"])
        self.mock_chapter_3 = self._create_mock_entity(
            3, "Test Chapter 3", ["peter_jones", "peter jones"]
        )
        self.mock_chapter_4 = self._create_mock_entity(4, "Fuzzy Chapter", ["Jone Doe"])
        self.mock_chapter.objects.all.return_value = [
            self.mock_chapter_1,
            self.mock_chapter_2,
            self.mock_chapter_3,
            self.mock_chapter_4,
        ]

        self.mock_committee_1 = self._create_mock_entity(101, "Test Committee", ["john.doe"])
        self.mock_committee.objects.all.return_value = [self.mock_committee_1]

        self.mock_content_type.objects.get_for_model.return_value = MagicMock()

    def _create_mock_entity(self, pk, name, leaders_raw):
        """Create a mock entity object."""
        mock_entity = MagicMock()
        mock_entity.pk = pk
        mock_entity.leaders_raw = leaders_raw
        mock_entity.__str__.return_value = name
        return mock_entity

    def test_command_with_invalid_model_name(self):
        """Test that the command raises an error for an invalid model name."""
        with pytest.raises(CommandError):
            call_command("owasp_update_leaders", "invalid_model")

    def test_exact_and_fuzzy_matches(self):
        """Test exact and fuzzy matching for chapters."""
        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        mock_bulk_create = self.mock_entity_member.objects.bulk_create
        assert mock_bulk_create.called

        call_args_list = mock_bulk_create.call_args[0][0]

        assert len(call_args_list) == 4
        created_members = {(m.entity_id, m.member_id) for m in call_args_list}

        assert (1, 1) in created_members
        assert (3, 3) in created_members
        assert (4, 1) in created_members
        assert (2, 2) in created_members

    def test_fuzzy_match_below_threshold(self):
        """Test that a fuzzy match is not found when the score is below the threshold."""
        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", "--threshold=95", stdout=out)

        mock_bulk_create = self.mock_entity_member.objects.bulk_create
        assert mock_bulk_create.called
        call_args_list = mock_bulk_create.call_args[0][0]

        assert len(call_args_list) == 3
        created_members = {(m.entity_id, m.member_id) for m in call_args_list}
        assert (4, 2) not in created_members

    def test_is_valid_user_filtering(self):
        """Test that users who do not meet the minimum length requirements are filtered out."""
        mock_invalid_chapter = self._create_mock_entity(99, "Invalid Chapter", ["a"])
        self.mock_chapter.objects.all.return_value = [mock_invalid_chapter]

        out = io.StringIO()
        call_command("owasp_update_leaders", "chapter", stdout=out)

        assert not self.mock_entity_member.objects.bulk_create.called
        assert "No new leader records to create" in out.getvalue()

    @patch(f"{COMMAND_PATH}.fuzz")
    def test_exact_match_is_preferred_over_fuzzy(self, mock_fuzz):
        """Test that if an exact match is found, fuzzy matching is not performed."""
        out = io.StringIO()
        call_command("owasp_update_leaders", "committee", stdout=out)

        assert not mock_fuzz.token_sort_ratio.called
        assert "Created 1 new leader records" in out.getvalue()
