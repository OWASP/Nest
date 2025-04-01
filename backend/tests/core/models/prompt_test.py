"""Tests for the Prompt model."""

import os
from unittest.mock import MagicMock, patch

import pytest

from apps.core.models.prompt import Prompt

OPEN_AI_SECRET_KEY_VALID = os.getenv("OPEN_AI_SECRET_KEY_VALID", "default_valid_key")
OPEN_AI_SECRET_KEY_NONE = os.getenv("OPEN_AI_SECRET_KEY_NONE", "default_none_key")


class TestPrompt:
    """Test the Prompt model."""

    def test_str(self):
        """Test the string representation of a prompt."""
        prompt = Prompt(name="Test Prompt")
        assert str(prompt) == "Test Prompt"

    @patch("django.db.models.Model.save")
    def test_save(self, mock_super_save):
        """Test the save method with key generation."""
        prompt = Prompt(name="Test Prompt", text="Test text")
        prompt.key = ""
        prompt.save()

        assert prompt.key == "test-prompt"

        mock_super_save.assert_called_once()

        mock_super_save.reset_mock()

        prompt = Prompt(name="Test Prompt 2", key="custom-key", text="Test text")
        prompt.save()

        assert prompt.key == "test-prompt-2"

        mock_super_save.assert_called_once()

    @patch("apps.core.models.prompt.Prompt.objects.get")
    @patch("apps.core.models.prompt.settings")
    @patch("apps.core.models.prompt.logger")
    def test_get_text_nonexistent_key_with_openai(self, mock_logger, mock_settings, mock_get):
        """Test get_text method for nonexistent key when OpenAI is enabled."""
        mock_settings.OPEN_AI_SECRET_KEY = OPEN_AI_SECRET_KEY_VALID
        mock_get.side_effect = Prompt.DoesNotExist

        result = Prompt.get_text("nonexistent")
        assert result is None
        mock_logger.warning.assert_called_once_with(
            "Prompt with key '%s' does not exist.", "nonexistent"
        )

    @patch("apps.core.models.prompt.Prompt.objects.get")
    @patch("apps.core.models.prompt.settings")
    @patch("apps.core.models.prompt.logger")
    def test_get_text_nonexistent_key_without_openai(self, mock_logger, mock_settings, mock_get):
        """Test get_text method for nonexistent key when OpenAI is disabled."""
        mock_settings.OPEN_AI_SECRET_KEY = OPEN_AI_SECRET_KEY_NONE
        mock_get.side_effect = Prompt.DoesNotExist

        result = Prompt.get_text("nonexistent")
        assert result is None
        mock_logger.warning.assert_not_called()

    @patch("apps.core.models.prompt.Prompt.objects.get")
    def test_get_text_existing_key(self, mock_get):
        """Test get_text method for existing key."""
        mock_prompt = MagicMock(text="Sample prompt text")
        mock_get.return_value = mock_prompt

        result = Prompt.get_text("existing")
        assert result == "Sample prompt text"
        mock_get.assert_called_once_with(key="existing")

    @pytest.mark.parametrize(
        ("method_name", "key"),
        [
            ("get_github_issue_hint", "github-issue-hint"),
            (
                "get_github_issue_documentation_project_summary",
                "github-issue-documentation-project-summary",
            ),
            ("get_github_issue_project_summary", "github-issue-project-summary"),
            ("get_owasp_chapter_suggested_location", "owasp-chapter-suggested-location"),
            ("get_owasp_chapter_summary", "owasp-chapter-summary"),
            ("get_owasp_committee_summary", "owasp-committee-summary"),
            ("get_owasp_project_summary", "owasp-project-summary"),
        ],
    )
    def test_prompt_getter_methods(self, method_name, key):
        """Test all getter methods for different prompt types."""
        with patch("apps.core.models.prompt.Prompt.get_text") as mock_get_text:
            expected_text = f"Test {key} prompt"
            mock_get_text.return_value = expected_text

            method = getattr(Prompt, method_name)
            result = method()

            assert result == expected_text
            mock_get_text.assert_called_once_with(key)

    def test_all_getter_methods_with_mocks(self):
        """Test all getter methods with mocks to ensure 100% coverage."""
        with patch("apps.core.models.prompt.Prompt.get_text") as mock_get_text:
            mock_get_text.return_value = "Mocked text"

            assert Prompt.get_github_issue_hint() == "Mocked text"
            mock_get_text.assert_called_with("github-issue-hint")

            assert Prompt.get_github_issue_documentation_project_summary() == "Mocked text"
            mock_get_text.assert_called_with("github-issue-documentation-project-summary")

            assert Prompt.get_github_issue_project_summary() == "Mocked text"
            mock_get_text.assert_called_with("github-issue-project-summary")

            assert Prompt.get_owasp_chapter_suggested_location() == "Mocked text"
            mock_get_text.assert_called_with("owasp-chapter-suggested-location")

            assert Prompt.get_owasp_chapter_summary() == "Mocked text"
            mock_get_text.assert_called_with("owasp-chapter-summary")

            assert Prompt.get_owasp_committee_summary() == "Mocked text"
            mock_get_text.assert_called_with("owasp-committee-summary")

            assert Prompt.get_owasp_project_summary() == "Mocked text"
            mock_get_text.assert_called_with("owasp-project-summary")
