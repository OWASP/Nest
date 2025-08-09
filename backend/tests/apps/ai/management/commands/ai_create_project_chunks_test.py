"""Tests for the ai_create_project_chunks Django management command."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_project_chunks import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_project():
    """Return a mock Project instance."""
    project = Mock()
    project.id = 1
    project.key = "test-project"
    return project


class TestAiCreateProjectChunksCommand:
    """Test suite for the ai_create_project_chunks command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Create chunks for OWASP project data"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 3
        parser.add_argument.assert_any_call(
            "--project-key",
            type=str,
            help="Process only the project with this key",
        )
        parser.add_argument.assert_any_call(
            "--all",
            action="store_true",
            help="Process all the projects",
        )
        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=50,
            help="Number of projects to process in each batch",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_handle_missing_openai_key(self, command):
        """Test command fails when OpenAI API key is not set."""
        command.stdout = MagicMock()
        command.style = MagicMock()

        command.handle()

        command.stdout.write.assert_called_once()
        command.style.ERROR.assert_called_once_with(
            "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
        )

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_project_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_project_chunks.Project.objects")
    def test_handle_no_projects_found(self, mock_project_objects, mock_openai, command):
        """Test command when no projects are found."""
        command.stdout = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_project_objects.filter.return_value = mock_queryset

        command.handle(project_key=None, all=False, batch_size=50)

        command.stdout.write.assert_called_with("No projects found to process")

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_project_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_project_chunks.Project.objects")
    def test_handle_with_project_key(
        self, mock_project_objects, mock_openai, command, mock_project
    ):
        """Test command with specific project key."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_project])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_project]
        mock_project_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_chunks_batch", return_value=1):
            command.handle(project_key="test-project", all=False, batch_size=50)

        mock_project_objects.filter.assert_called_with(key="test-project")

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_project_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_project_chunks.Project.objects")
    def test_handle_with_all_flag(self, mock_project_objects, mock_openai, command, mock_project):
        """Test command with --all flag."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_project])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_project]
        mock_project_objects.all.return_value = mock_queryset

        with patch.object(command, "process_chunks_batch", return_value=1):
            command.handle(project_key=None, all=True, batch_size=50)

        mock_project_objects.all.assert_called_once()

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_project_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_project_chunks.Project.objects")
    def test_handle_default_active_projects(
        self, mock_project_objects, mock_openai, command, mock_project
    ):
        """Test command defaults to active projects."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_project])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_project]
        mock_project_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_chunks_batch", return_value=1):
            command.handle(project_key=None, all=False, batch_size=50)

        mock_project_objects.filter.assert_called_with(is_active=True)
