from unittest.mock import MagicMock, patch

import pytest
from psycopg2 import sql

from apps.common.management.commands.purge_data import Command


@pytest.mark.parametrize(
    ("nest_apps", "mock_models"),
    [
        (
            ["github", "owasp", "slack"],
            {
                "github": ["Issue", "Repository"],
                "owasp": ["Chapter", "Project"],
                "slack": ["Conversation", "Member", "Workspace"],
            },
        )
    ],
)
class TestPurgeDataCommand:
    @patch("apps.common.management.commands.purge_data.apps.get_app_config")
    @patch("apps.common.management.commands.purge_data.connection.cursor")
    def test_handle(self, mock_cursor, mock_get_app_config, nest_apps, mock_models):
        mock_cursor.return_value.__enter__.return_value = MagicMock()
        cursor_instance = mock_cursor.return_value.__enter__.return_value

        def get_app_config_side_effect(app_name):
            mock_app_config = MagicMock()
            mock_app_config.get_models.return_value = [
                MagicMock(
                    __name__=model,
                    _meta=MagicMock(
                        db_table=f"{app_name.lower()}_{model.lower()}",
                        model_name=f"{model}s",
                    ),
                )
                for model in mock_models[app_name]
            ]
            return mock_app_config

        mock_get_app_config.side_effect = get_app_config_side_effect

        command = Command()
        command.stdout = MagicMock()
        command.handle()

        for app_name in nest_apps:
            for model_name in mock_models[app_name]:
                table_name = f"{app_name.lower()}_{model_name.lower()}"
                expected_query = sql.SQL("TRUNCATE TABLE {} CASCADE").format(
                    sql.Identifier(table_name)
                )
                cursor_instance.execute.assert_any_call(expected_query)
                command.stdout.write.assert_any_call(f"Purged {app_name}.{model_name}")
