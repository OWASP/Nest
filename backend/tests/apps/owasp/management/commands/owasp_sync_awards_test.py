"""Tests for owasp_sync_awards management command."""

from unittest.mock import patch

from django.test import TestCase

from apps.owasp.management.commands.owasp_sync_awards import Command
from apps.owasp.models.award import Award


class OwaspSyncAwardsTest(TestCase):
    """Test owasp_sync_awards command."""

    @patch("apps.owasp.management.commands.owasp_sync_awards.get_repository_file_content")
    def test_sync_awards(self, mock_get_content):
        """Test syncing awards from YAML data."""
        mock_get_content.return_value = """
- title: WASPY
  type: category
  description: Test category
- title: Project Person of the Year
  type: award
  category: WASPY
  year: 2024
  winners:
    - name: Test Winner
      info: Test winner info
"""

        command = Command()
        command.handle()

        # Check that award was created
        award = Award.objects.get(name="Project Person of the Year - Test Winner (2024)")
        assert award.category == "WASPY"
        assert award.year == 2024
        assert award.description == "Test winner info"
