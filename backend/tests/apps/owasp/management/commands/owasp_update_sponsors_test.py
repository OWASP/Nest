"""Test suite for the owasp_update_sponsors command."""

import io
from unittest.mock import Mock, call, patch

import pytest
import yaml
from django.core.management import call_command

from apps.owasp.management.commands.owasp_update_sponsors import Command
from apps.owasp.models.sponsor import Sponsor


class TestOWASPUpdateSponsorsCommand:
    """Test suite for the OWASP update sponsors command."""

    @pytest.fixture
    def mock_stdout(self):
        """Return a StringIO instance to capture command output."""
        return io.StringIO()

    @pytest.fixture
    def sample_sponsors_data(self):
        """Return sample sponsors data for testing."""
        return [
            {"name": "Sponsor 1", "url": "https://sponsor1.com", "level": "Diamond"},
            {"name": "Sponsor 2", "url": "https://sponsor2.com", "level": "Gold"},
            {"name": "Sponsor 3", "url": "https://sponsor3.com", "level": "Silver"},
        ]

    @patch("apps.owasp.management.commands.owasp_update_sponsors.get_repository_file_content")
    @patch("apps.owasp.management.commands.owasp_update_sponsors.Sponsor")
    def test_handle_fetches_and_processes_sponsors(
        self, mock_sponsor, mock_get_repo_content, sample_sponsors_data, mock_stdout
    ):
        """Test that the handle method fetches and processes sponsors correctly."""
        mock_get_repo_content.return_value = yaml.dump(sample_sponsors_data)
        mock_sponsor.update_data = lambda sponsor: sponsor
        mock_sponsor.bulk_save = Mock()

        call_command("owasp_update_sponsors", stdout=mock_stdout)

        mock_get_repo_content.assert_called_once_with(
            "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/corp_members.yml"
        )

        mock_sponsor.bulk_save.assert_called_once()
        sponsors_arg = mock_sponsor.bulk_save.call_args[0][0]
        assert len(sponsors_arg) == len(sample_sponsors_data)
        for sponsor in sponsors_arg:
            assert sponsor in sample_sponsors_data

    @patch("apps.owasp.management.commands.owasp_update_sponsors.get_repository_file_content")
    @patch("apps.owasp.management.commands.owasp_update_sponsors.yaml.safe_load")
    @patch("apps.owasp.management.commands.owasp_update_sponsors.Sponsor")
    def test_yaml_parsing(
        self, mock_sponsor, mock_yaml_safe_load, mock_get_repo_content, sample_sponsors_data
    ):
        """Test that the YAML data is parsed correctly."""
        mock_get_repo_content.return_value = "dummy yaml content"
        mock_yaml_safe_load.return_value = sample_sponsors_data
        mock_sponsor.update_data = lambda sponsor: sponsor
        mock_sponsor.bulk_save = Mock()

        command = Command()
        command.handle()

        mock_yaml_safe_load.assert_called_once_with(mock_get_repo_content.return_value)

    @patch("apps.owasp.management.commands.owasp_update_sponsors.get_repository_file_content")
    @patch("apps.owasp.management.commands.owasp_update_sponsors.Sponsor")
    def test_sponsor_update_data_called(
        self, mock_sponsor, mock_get_repo_content, sample_sponsors_data
    ):
        """Test that Sponsor.update_data is called for each sponsor."""
        mock_get_repo_content.return_value = yaml.dump(sample_sponsors_data)
        mock_sponsor.update_data = Mock(side_effect=lambda s: s)
        mock_sponsor.bulk_save = Mock()

        command = Command()
        command.handle()

        assert mock_sponsor.update_data.call_count == len(sample_sponsors_data)
        mock_sponsor.update_data.assert_has_calls(
            [call(sponsor) for sponsor in sample_sponsors_data]
        )

    @patch("apps.owasp.management.commands.owasp_update_sponsors.get_repository_file_content")
    def test_handle_with_empty_sponsors_data(self, mock_get_repo_content):
        """Test handling when empty sponsors data is returned."""
        mock_get_repo_content.return_value = yaml.dump([])

        with patch.object(Sponsor, "bulk_save") as mock_bulk_save:
            command = Command()
            command.handle()

            mock_bulk_save.assert_called_once()
            assert mock_bulk_save.call_args[0][0] == []

    @patch("apps.owasp.management.commands.owasp_update_sponsors.get_repository_file_content")
    def test_expandtabs_called_on_content(self, mock_get_repo_content):
        """Test that expandtabs is called on the content."""
        content_mock = Mock()
        mock_get_repo_content.return_value = content_mock

        with (
            patch(
                "apps.owasp.management.commands.owasp_update_sponsors.yaml.safe_load"
            ) as mock_yaml_safe_load,
            patch.object(Sponsor, "bulk_save"),
        ):
            command = Command()
            command.handle()

            content_mock.expandtabs.assert_called_once()
            mock_yaml_safe_load.assert_called_once_with(content_mock.expandtabs.return_value)

            content_mock.expandtabs.reset_mock()
            command.handle()
            content_mock.expandtabs.assert_called_once_with()
