from unittest.mock import MagicMock, patch

import pytest

from apps.common.management.commands.load_data import Command


@pytest.mark.parametrize("nest_apps", [("github", "owasp")])
class TestLoadDataCommand:
    @patch("apps.common.management.commands.load_data.apps.get_app_config")
    @patch("apps.common.management.commands.load_data.unregister")
    @patch("apps.common.management.commands.load_data.register")
    @patch("apps.common.management.commands.load_data.call_command")
    @patch("apps.common.management.commands.load_data.transaction.atomic")
    def test_handle(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
        mock_get_app_config,
        nest_apps,
    ):
        mock_model = MagicMock()
        mock_app_config = MagicMock()
        mock_app_config.get_models.return_value = [mock_model]
        mock_get_app_config.return_value = mock_app_config

        mock_atomic.return_value.__enter__ = MagicMock()
        mock_atomic.return_value.__exit__ = MagicMock()

        mock_unregister.return_value = None
        mock_register.return_value = None

        command = Command()
        command.handle()

        for app in nest_apps:
            mock_get_app_config.assert_any_call(app)
            mock_app_config.get_models.assert_any_call()

        mock_call_command.assert_called_once_with("loaddata", "data/nest.json", "-v", "3")

        mock_register.assert_called_with(mock_model)
