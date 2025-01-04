from unittest.mock import patch

from apps.common.management.commands.clear_cache import Command


class TestClearCacheCommand:
    @patch("django.core.cache.cache.clear")
    def test_handle(self, mock_clear_cache):
        command = Command()
        command.handle()

        mock_clear_cache.assert_called_once()
