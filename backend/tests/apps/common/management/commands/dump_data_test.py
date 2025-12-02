from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import override_settings

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "db-name",
        "USER": "db-user",
        "PASSWORD": "db-pass",
        "HOST": "db-host",
        "PORT": "5432",
    }
}


class TestDumpDataCommand:
    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    @patch("apps.common.management.commands.dump_data.sql")
    def test_dump_data(self, mock_sql, mock_path, mock_connect, mock_run):
        # Mock psycopg2 connection/cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("public.users",), ("public.members",)]
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve
        mock_sql.SQL.return_value.format.return_value = "UPDATE public.users SET email = '';"
        call_command(
            "dump_data",
            "--output",
            "data/dump.sql.gz",
        )

        # Verify temp DB created from template
        expected_temp_db = "temp_db-name"
        mock_connect.assert_any_call(
            dbname="postgres",
            user="db-user",
            # ruff: noqa: S106
            password="db-pass",
            host="db-host",
            port="5432",
        )
        mock_cursor.execute.assert_any_call(
            f"CREATE DATABASE {expected_temp_db} TEMPLATE db-name;"
        )
        executed_sql = [str(c.args[0]) for c in mock_cursor.execute.call_args_list]
        assert "UPDATE public.users SET email = '';" in executed_sql
        assert (
            """
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'email';
        """
            in executed_sql
        )

        print(mock_run.call_args[0][0])
        assert [
            "pg_dump",
            "-h",
            "db-host",
            "-p",
            "5432",
            "-U",
            "db-user",
            "-d",
            expected_temp_db,
            "--compress=9",
            "--clean",
            "--table=public.owasp_*",
            "--table=public.github_*",
            "--table=public.slack_members",
            "--table=public.slack_workspaces",
            "--table=public.slack_conversations",
            "--table=public.slack_messages",
            "-f",
            str(mock_resolve),
        ] == mock_run.call_args[0][0]
        # Ensure DROP DATABASE executed at the end
        mock_cursor.execute.assert_any_call(f"DROP DATABASE IF EXISTS {expected_temp_db};")
        mock_path.return_value.resolve.assert_called_once()
        mock_resolve.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
