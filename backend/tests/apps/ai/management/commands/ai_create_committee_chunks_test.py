from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_committee_chunks import Command


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_committee():
    committee = Mock()
    committee.id = 1
    committee.key = "test-committee"
    return committee


class TestAiCreateCommitteeChunksCommand:
    def test_command_inheritance(self, command):
        assert isinstance(command, BaseCommand)

    def test_model_class_property(self, command):
        from apps.owasp.models.committee import Committee

        assert command.model_class == Committee

    def test_entity_name_property(self, command):
        assert command.entity_name == "committee"

    def test_entity_name_plural_property(self, command):
        assert command.entity_name_plural == "committees"

    def test_key_field_name_property(self, command):
        assert command.key_field_name == "key"

    def test_extract_content(self, command, mock_committee):
        with patch(
            "apps.ai.management.commands.ai_create_committee_chunks.extract_committee_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_committee)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_committee)
