import json
from unittest.mock import Mock

import pytest

from apps.owasp.management.commands.owasp_sync_board_candidates import Command


class TestSyncBoardCandidatesCommand:
    @pytest.fixture
    def command(self, mocker):
        cmd = Command()
        cmd.stdout = Mock()
        cmd.stderr = Mock()
        cmd.style = Mock()

        # Mock ContentType to avoid DB connection errors during tests using GenericForeignKeys
        from django.contrib.contenttypes.models import ContentType

        mock_ct = ContentType(app_label="owasp", model="boardofdirectors")
        mock_ct.id = 1
        mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        return cmd

    def test_get_candidate_name_from_filename(self, command):
        assert command.get_candidate_name_from_filename("john-doe.md") == "John Doe"
        assert command.get_candidate_name_from_filename("jane_smith.md") == "Jane Smith"
        assert (
            command.get_candidate_name_from_filename("mary-ann-johnson.md") == "Mary Ann Johnson"
        )
        assert command.get_candidate_name_from_filename("Candidate-Name.md") == "Candidate Name"

    def test_parse_candidate_metadata_valid(self, command):
        content = """---
name: John Doe
email: john.doe@example.com
title: Software Security Professional
---

# Candidate Statement

I am running for the OWASP Board of Directors."""

        metadata = command.parse_candidate_metadata(content)

        assert metadata["name"] == "John Doe"
        assert metadata["email"] == "john.doe@example.com"
        assert metadata["title"] == "Software Security Professional"

    def test_parse_candidate_metadata_no_frontmatter(self, command):
        content = "# Just a heading\n\nSome content"
        metadata = command.parse_candidate_metadata(content)
        assert metadata == {}

    def test_parse_candidate_metadata_invalid_yaml(self, command):
        content = """---
name: John Doe
invalid: [unclosed
---

Content"""

        metadata = command.parse_candidate_metadata(content)
        assert metadata == {}

    def test_sync_year_candidates_success(self, command, mocker):
        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content"
        )

        mock_board = Mock()
        mock_board.id = 100
        mock_board_manager = Mock()
        mock_board_manager.get_or_create.return_value = (mock_board, True)
        mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects", mock_board_manager
        )

        mock_update_data = mocker.patch("apps.owasp.models.entity_member.EntityMember.update_data")

        repo_files = [{"name": "jane-doe.md", "download_url": "https://github.com/jane-doe.md"}]

        file_content = "---\nname: Jane Doe\nemail: jane@example.com\n---\nBio"

        def side_effect(url):
            if "contents/2024" in url:
                return json.dumps(repo_files)
            if "jane-doe.md" in url:
                return file_content
            return ""

        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            side_effect=side_effect,
        )

        count = command.sync_year_candidates(2024)

        assert count == 1
        mock_update_data.assert_called_once()
        args, kwargs = mock_update_data.call_args
        data_arg = args[0]
        assert kwargs["save"] is True
        assert data_arg["member_name"] == "Jane Doe"

    def test_sync_year_candidates_api_error(self, command, mocker):
        mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create",
            return_value=(Mock(), True),
        )

        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            side_effect=OSError("API Error"),
        )

        count = command.sync_year_candidates(2024)
        assert count == 0
        command.stderr.write.assert_called()

    def test_handle_specific_year(self, command, mocker):
        mock_sync = mocker.patch.object(command, "sync_year_candidates", return_value=5)

        command.handle(year=2025)

        mock_sync.assert_called_with(2025)
        command.stdout.write.assert_called_with(mocker.ANY)

    def test_handle_all_years(self, command, mocker):
        mock_sync = mocker.patch.object(command, "sync_year_candidates", return_value=2)

        files_json = json.dumps(
            [
                {"name": "2024", "type": "dir"},
                {"name": "2025", "type": "dir"},
                {"name": "README.md", "type": "file"},
            ]
        )
        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            return_value=files_json,
        )

        command.handle()

        assert mock_sync.call_count == 2
        mock_sync.assert_any_call(2024)
        mock_sync.assert_any_call(2025)
