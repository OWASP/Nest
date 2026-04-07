"""Tests for chapter signal handlers."""

from unittest.mock import MagicMock, patch

from apps.owasp.signals.chapter import chapter_post_save


class TestChapterSignals:
    """Test chapter post_save signal handler."""

    @patch("apps.owasp.signals.chapter.transaction.on_commit", side_effect=lambda f: f())
    @patch("apps.owasp.signals.chapter.publish_chapter_notification")
    def test_chapter_created_publishes_created_notification(self, mock_publish, mock_on_commit):
        """Test that creating a chapter publishes a 'created' notification."""
        chapter = MagicMock()
        chapter_post_save(sender=None, instance=chapter, created=True)
        mock_publish.assert_called_once_with(chapter, "created")
        mock_on_commit.assert_called_once()

    @patch("apps.owasp.signals.chapter.transaction.on_commit", side_effect=lambda f: f())
    @patch("apps.owasp.signals.chapter.publish_chapter_notification")
    def test_chapter_updated_no_changes_skips_notification(self, mock_publish, mock_on_commit):
        """Test that updating a chapter with no changes skips notification."""
        chapter = MagicMock()
        # Set up previous values that match current values - no changes, no notification
        chapter._previous_values = {
            "name": "Test Chapter",
            "country": "Test Country",
            "region": "Test Region",
            "suggested_location": "Test Location",
            "description": "Test description",
        }
        # Set current values to be the same - no notification should be sent
        chapter.name = "Test Chapter"
        chapter.country = "Test Country"
        chapter.region = "Test Region"
        chapter.suggested_location = "Test Location"
        chapter.description = "Test description"
        chapter_post_save(sender=None, instance=chapter, created=False)
        # No changes, so no notification should be published
        mock_publish.assert_not_called()
        mock_on_commit.assert_not_called()

    @patch("apps.owasp.signals.chapter.transaction.on_commit", side_effect=lambda f: f())
    @patch("apps.owasp.signals.chapter.publish_chapter_notification")
    def test_chapter_updated_publishes_updated_notification(self, mock_publish, mock_on_commit):
        """Test that updating a chapter publishes an 'updated' notification."""
        chapter = MagicMock()
        chapter._previous_values = {
            "name": "Test Chapter",
            "country": "Test Country",
            "region": "Test Region",
            "suggested_location": "Test Location",
            "description": "Test description",
        }
        # Change a meaningful field
        chapter.name = "New Test Chapter Name"
        chapter.country = "Test Country"
        chapter.region = "Test Region"
        chapter.suggested_location = "Test Location"
        chapter.description = "Test description"

        chapter_post_save(sender=None, instance=chapter, created=False)

        expected_changed_fields = {
            "name": {
                "old": "Test Chapter",
                "new": "New Test Chapter Name",
            }
        }
        mock_publish.assert_called_once_with(chapter, "updated", expected_changed_fields)
        mock_on_commit.assert_called_once()
