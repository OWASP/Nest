"""Tests for Prompt model."""

from unittest.mock import MagicMock, patch

from apps.core.models.prompt import Prompt


class TestPromptModel:
    """Test cases for Prompt model."""

    def test_str(self):
        """Test string representation returns name."""
        prompt = Prompt(name="Test Prompt", key="test-prompt")
        assert str(prompt) == "Test Prompt"

    def test_save_generates_key(self):
        """Test that save auto-generates key from name."""
        prompt = Prompt(name="My Test Prompt")

        with patch.object(Prompt.__bases__[0], "save"):
            prompt.save()

        assert prompt.key == "my-test-prompt"

    def test_save_generates_key_with_special_chars(self):
        """Test key generation handles special characters."""
        prompt = Prompt(name="Test Prompt! With @Special# Chars")

        with patch.object(Prompt.__bases__[0], "save"):
            prompt.save()

        assert prompt.key == "test-prompt-with-special-chars"

    def test_get_text_exists(self):
        """Test get_text returns text for existing prompt."""
        with patch.object(Prompt, "objects") as mock_objects:
            mock_prompt = MagicMock()
            mock_prompt.text = "This is the prompt text"
            mock_objects.get.return_value = mock_prompt

            result = Prompt.get_text("test-key")

        assert result == "This is the prompt text"
        mock_objects.get.assert_called_once_with(key="test-key")

    def test_get_text_not_exists(self):
        """Test get_text returns empty string when prompt not found."""
        with (
            patch.object(Prompt, "objects") as mock_objects,
            patch("apps.core.models.prompt.settings") as mock_settings,
            patch("apps.core.models.prompt.logger") as mock_logger,
        ):
            mock_objects.get.side_effect = Prompt.DoesNotExist
            mock_settings.OPEN_AI_SECRET_KEY = "real-key"  # noqa: S105

            result = Prompt.get_text("nonexistent-key")

        assert result == ""
        mock_logger.warning.assert_called_once()

    def test_get_text_not_exists_no_warning_when_no_api_key(self):
        """Test get_text doesn't log warning when OPEN_AI_SECRET_KEY is None."""
        with (
            patch.object(Prompt, "objects") as mock_objects,
            patch("apps.core.models.prompt.settings") as mock_settings,
            patch("apps.core.models.prompt.logger") as mock_logger,
        ):
            mock_objects.get.side_effect = Prompt.DoesNotExist
            mock_settings.OPEN_AI_SECRET_KEY = "None"  # noqa: S105

            result = Prompt.get_text("nonexistent-key")

        assert result == ""
        mock_logger.warning.assert_not_called()

    def test_get_evaluator_system_prompt(self):
        """Test get_evaluator_system_prompt calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="evaluator text") as mock_get_text:
            result = Prompt.get_evaluator_system_prompt()

        assert result == "evaluator text"
        mock_get_text.assert_called_once_with("evaluator-system-prompt")

    def test_get_github_issue_hint(self):
        """Test get_github_issue_hint calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="hint text") as mock_get_text:
            result = Prompt.get_github_issue_hint()

        assert result == "hint text"
        mock_get_text.assert_called_once_with("github-issue-hint")

    def test_get_github_issue_documentation_project_summary(self):
        """Test get_github_issue_documentation_project_summary."""
        with patch.object(Prompt, "get_text", return_value="doc summary") as mock_get_text:
            result = Prompt.get_github_issue_documentation_project_summary()

        assert result == "doc summary"
        mock_get_text.assert_called_once_with("github-issue-documentation-project-summary")

    def test_get_github_issue_project_summary(self):
        """Test get_github_issue_project_summary calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="project summary") as mock_get_text:
            result = Prompt.get_github_issue_project_summary()

        assert result == "project summary"
        mock_get_text.assert_called_once_with("github-issue-project-summary")

    def test_get_metadata_extractor_prompt(self):
        """Test get_metadata_extractor_prompt calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="extractor text") as mock_get_text:
            result = Prompt.get_metadata_extractor_prompt()

        assert result == "extractor text"
        mock_get_text.assert_called_once_with("metadata-extractor-prompt")

    def test_get_owasp_chapter_suggested_location(self):
        """Test get_owasp_chapter_suggested_location."""
        with patch.object(Prompt, "get_text", return_value="location text") as mock_get_text:
            result = Prompt.get_owasp_chapter_suggested_location()

        assert result == "location text"
        mock_get_text.assert_called_once_with("owasp-chapter-suggested-location")

    def test_get_owasp_chapter_summary(self):
        """Test get_owasp_chapter_summary calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="chapter summary") as mock_get_text:
            result = Prompt.get_owasp_chapter_summary()

        assert result == "chapter summary"
        mock_get_text.assert_called_once_with("owasp-chapter-summary")

    def test_get_owasp_committee_summary(self):
        """Test get_owasp_committee_summary calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="committee summary") as mock_get_text:
            result = Prompt.get_owasp_committee_summary()

        assert result == "committee summary"
        mock_get_text.assert_called_once_with("owasp-committee-summary")

    def test_get_owasp_event_suggested_location(self):
        """Test get_owasp_event_suggested_location."""
        with patch.object(Prompt, "get_text", return_value="event location") as mock_get_text:
            result = Prompt.get_owasp_event_suggested_location()

        assert result == "event location"
        mock_get_text.assert_called_once_with("owasp-event-suggested-location")

    def test_get_owasp_event_summary(self):
        """Test get_owasp_event_summary calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="event summary") as mock_get_text:
            result = Prompt.get_owasp_event_summary()

        assert result == "event summary"
        mock_get_text.assert_called_once_with("owasp-event-summary")

    def test_get_owasp_project_summary(self):
        """Test get_owasp_project_summary calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="project summary") as mock_get_text:
            result = Prompt.get_owasp_project_summary()

        assert result == "project summary"
        mock_get_text.assert_called_once_with("owasp-project-summary")

    def test_get_rag_system_prompt(self):
        """Test get_rag_system_prompt calls get_text with correct key."""
        with patch.object(Prompt, "get_text", return_value="rag prompt") as mock_get_text:
            result = Prompt.get_rag_system_prompt()

        assert result == "rag prompt"
        mock_get_text.assert_called_once_with("rag-system-prompt")

    def test_get_slack_question_detector_prompt(self):
        """Test get_slack_question_detector_prompt."""
        with patch.object(Prompt, "get_text", return_value="slack prompt") as mock_get_text:
            result = Prompt.get_slack_question_detector_prompt()

        assert result == "slack prompt"
        mock_get_text.assert_called_once_with("slack-question-detector-system-prompt")
