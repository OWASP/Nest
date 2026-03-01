import json
from argparse import ArgumentParser
from unittest.mock import Mock

import pytest
from django.contrib.contenttypes.models import ContentType

from apps.owasp.management.commands.owasp_sync_board_candidates import Command


class TestSyncBoardCandidatesCommand:
    @pytest.fixture
    def command(self, mocker):
        cmd = Command()
        cmd.stdout = Mock()
        cmd.stderr = Mock()
        cmd.style = Mock()

        mock_ct = ContentType(app_label="owasp", model="boardofdirectors")
        mock_ct.id = 1
        mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        return cmd

    def test_add_arguments(self, command):
        """Test add_arguments adds expected arguments."""
        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args([])
        assert args.year is None

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

    def test_parse_candidate_metadata_no_yaml_match(self, command):
        """Test parse_candidate_metadata when content starts with --- but regex doesn't match."""
        content = "---\nfoo: bar\n"
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
        assert kwargs["save"]
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

    def test_handle_all_years_error(self, command, mocker):
        """Test handle all years when repository structure fetch fails."""
        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            return_value="not valid json",
        )

        command.handle(year=None)

        command.stderr.write.assert_called()

    def test_sync_year_candidates_skip_non_md(self, command, mocker):
        """Test sync_year_candidates skips non-.md files."""
        mock_board = Mock()
        mock_board.id = 100
        mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create",
            return_value=(mock_board, True),
        )
        mock_update_data = mocker.patch("apps.owasp.models.entity_member.EntityMember.update_data")

        repo_files = [
            {"name": "readme.txt", "download_url": "https://example.com/readme.txt"},
        ]

        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            return_value=json.dumps(repo_files),
        )

        count = command.sync_year_candidates(2024)
        assert count == 0
        mock_update_data.assert_not_called()

    def test_sync_year_candidates_skip_info_md(self, command, mocker):
        """Test sync_year_candidates skips info.md."""
        mock_board = Mock()
        mock_board.id = 100
        mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create",
            return_value=(mock_board, True),
        )
        mock_update_data = mocker.patch("apps.owasp.models.entity_member.EntityMember.update_data")

        repo_files = [
            {"name": "info.md", "download_url": "https://example.com/info.md"},
        ]

        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            return_value=json.dumps(repo_files),
        )

        count = command.sync_year_candidates(2024)
        assert count == 0
        mock_update_data.assert_not_called()

    def test_sync_year_candidates_no_download_url(self, command, mocker):
        """Test sync_year_candidates skips files without download_url."""
        mock_board = Mock()
        mock_board.id = 100
        mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create",
            return_value=(mock_board, True),
        )
        mock_update_data = mocker.patch("apps.owasp.models.entity_member.EntityMember.update_data")

        repo_files = [
            {"name": "candidate.md"},
        ]

        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            return_value=json.dumps(repo_files),
        )

        count = command.sync_year_candidates(2024)
        assert count == 0
        mock_update_data.assert_not_called()

    def test_sync_year_candidates_no_candidate_name(self, command, mocker):
        """Test sync_year_candidates warns when no candidate name found."""
        mock_board = Mock()
        mock_board.id = 100
        mocker.patch(
            "apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create",
            return_value=(mock_board, True),
        )
        mock_update_data = mocker.patch("apps.owasp.models.entity_member.EntityMember.update_data")

        repo_files = [
            {"name": ".md", "download_url": "https://example.com/.md"},
        ]

        def side_effect(url):
            if "contents/2024" in url:
                return json.dumps(repo_files)
            return "---\n---\n"

        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_candidates.get_repository_file_content",
            side_effect=side_effect,
        )

        count = command.sync_year_candidates(2024)
        assert count == 0
        mock_update_data.assert_not_called()
        command.stderr.write.assert_called()
