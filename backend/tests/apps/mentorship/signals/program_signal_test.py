"""Tests for mentorship program signal handler."""

from unittest.mock import MagicMock, patch

from apps.mentorship.signals.program import program_post_save_clear_algolia_cache


class TestProgramPostSaveClearAlgoliaCache:
    """Tests for program_post_save_clear_algolia_cache signal."""

    @patch("apps.mentorship.signals.program.clear_index_cache")
    @patch("apps.mentorship.signals.program.logger")
    def test_clears_algolia_cache(self, mock_logger, mock_clear_cache):
        """Test signal clears the 'programs' Algolia index cache."""
        instance = MagicMock()
        instance.name = "Test Program"

        program_post_save_clear_algolia_cache(sender=None, instance=instance)

        mock_logger.info.assert_called_once_with(
            "Signal received for program '%s'. Clearing 'programs' index.",
            "Test Program",
        )
        mock_clear_cache.assert_called_once_with("programs")
