"""Tests for the owasp_generate_community_snapshot_video Django management command."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management.base import BaseCommand

sys.modules["weasyprint"] = MagicMock()

from apps.owasp.management.commands.owasp_generate_community_snapshot_video import (  # noqa: E402
    Command,
)


@pytest.fixture
def command():
    """Return a command instance."""
    cmd = Command()
    cmd.stdout = MagicMock()
    return cmd


class TestOwaspGenerateCommunitySnapshotVideoCommand:
    """Test suite for the owasp_generate_community_snapshot_video command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Generate OWASP community snapshot video."

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that add_arguments configures the parser correctly."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 2


@patch("pathlib.Path.mkdir")
@patch("apps.owasp.management.commands.owasp_generate_community_snapshot_video.VideoGenerator")
@patch("apps.owasp.management.commands.owasp_generate_community_snapshot_video.SlideBuilder")
@patch("apps.owasp.management.commands.owasp_generate_community_snapshot_video.Snapshot")
class TestHandleMethod:
    """Test suite for the handle method of the command."""

    @pytest.fixture
    def command(self):
        """Return a command instance with mocked stdout."""
        cmd = Command()
        cmd.stdout = MagicMock()
        return cmd

    def test_handle_no_snapshots_found(
        self,
        mock_snapshot,
        mock_slide_builder,
        mock_generator,
        mock_mkdir,
        command,
    ):
        """Test handle when no completed snapshots are found."""
        mock_snapshot.objects.filter.return_value.order_by.return_value = []

        with patch(
            "apps.owasp.management.commands.owasp_generate_community_snapshot_video.logger"
        ) as mock_logger:
            command.handle(snapshot_key="2025-01", output_dir="/output")

        mock_logger.error.assert_called_once()
        mock_slide_builder.assert_not_called()
        mock_generator.assert_not_called()

    def test_handle_with_valid_snapshots(
        self,
        mock_snapshot,
        mock_slide_builder,
        mock_generator,
        mock_mkdir,
        command,
    ):
        """Test handle with valid snapshots."""
        mock_snapshot_obj = Mock()
        mock_snapshot.objects.filter.return_value.order_by.return_value = [mock_snapshot_obj]
        mock_snapshot.Status.COMPLETED = "completed"

        mock_builder_instance = MagicMock()
        mock_slide_builder.return_value = mock_builder_instance

        mock_intro_slide = Mock()
        mock_sponsors_slide = Mock()
        mock_projects_slide = None
        mock_chapters_slide = Mock()
        mock_releases_slide = None
        mock_thank_you_slide = Mock()

        mock_builder_instance.add_intro_slide.return_value = mock_intro_slide
        mock_builder_instance.add_sponsors_slide.return_value = mock_sponsors_slide
        mock_builder_instance.add_projects_slide.return_value = mock_projects_slide
        mock_builder_instance.add_chapters_slide.return_value = mock_chapters_slide
        mock_builder_instance.add_releases_slide.return_value = mock_releases_slide
        mock_builder_instance.add_thank_you_slide.return_value = mock_thank_you_slide

        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance

        command.handle(snapshot_key="2025-01", output_dir="/output")

        mock_slide_builder.assert_called_once()
        mock_generator.assert_called_once()
        assert mock_generator_instance.append_slide.call_count == 4
        mock_generator_instance.generate_video.assert_called_once()
        args = mock_generator_instance.generate_video.call_args
        assert isinstance(args[0][0], Path)
        assert args[0][1] == "2025-01_snapshot"
        mock_generator_instance.cleanup.assert_called_once()

    def test_handle_filters_none_slides(
        self,
        mock_snapshot,
        mock_slide_builder,
        mock_generator,
        mock_mkdir,
        command,
    ):
        """Test that handle filters out None slides."""
        mock_snapshot_obj = Mock()
        mock_snapshot.objects.filter.return_value.order_by.return_value = [mock_snapshot_obj]
        mock_snapshot.Status.COMPLETED = "completed"

        mock_builder_instance = MagicMock()
        mock_slide_builder.return_value = mock_builder_instance

        mock_builder_instance.add_intro_slide.return_value = Mock()
        mock_builder_instance.add_sponsors_slide.return_value = None
        mock_builder_instance.add_projects_slide.return_value = None
        mock_builder_instance.add_chapters_slide.return_value = None
        mock_builder_instance.add_releases_slide.return_value = None
        mock_builder_instance.add_thank_you_slide.return_value = Mock()

        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance

        command.handle(snapshot_key="2025-01", output_dir="/output")

        assert mock_generator_instance.append_slide.call_count == 2

    def test_handle_prints_success_message(
        self,
        mock_snapshot,
        mock_slide_builder,
        mock_generator,
        mock_mkdir,
        command,
    ):
        """Test that handle prints success message with video path."""
        mock_snapshot_obj = Mock()
        mock_snapshot.objects.filter.return_value.order_by.return_value = [mock_snapshot_obj]
        mock_snapshot.Status.COMPLETED = "completed"

        mock_builder_instance = MagicMock()
        mock_slide_builder.return_value = mock_builder_instance
        mock_builder_instance.add_intro_slide.return_value = Mock()
        mock_builder_instance.add_sponsors_slide.return_value = Mock()
        mock_builder_instance.add_projects_slide.return_value = Mock()
        mock_builder_instance.add_chapters_slide.return_value = Mock()
        mock_builder_instance.add_releases_slide.return_value = Mock()
        mock_builder_instance.add_thank_you_slide.return_value = Mock()

        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_video.return_value = Path("/path/to/video.mkv")
        mock_generator.return_value = mock_generator_instance

        command.handle(snapshot_key="2025", output_dir="/output")

        stdout_calls = [str(call) for call in command.stdout.write.call_args_list]
        assert any("community_snapshot_video_2025" in call for call in stdout_calls)
