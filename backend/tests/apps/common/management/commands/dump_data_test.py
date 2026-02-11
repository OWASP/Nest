from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.test import override_settings
from psycopg2 import OperationalError, ProgrammingError, sql

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "db-name",
        "USER": "db-user",
        "PASSWORD": "db-pass",  # NOSONAR
        "HOST": "db-host",
        "PORT": "5432",
    }
}


class TestDumpDataCommand:
    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data(self, mock_path, mock_connect, mock_run):
        # Mock psycopg2 connection/cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("public.users",), ("public.members",)]
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve
        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
        )

        # Verify temp DB created from template
        expected_temp_db = "temp_db-name"
        mock_connect.assert_any_call(
            dbname="postgres",
            user="db-user",
            # ruff: noqa: S106
            password="db-pass",  # NOSONAR
            host="db-host",
            port="5432",
        )
        mock_cursor.execute.assert_any_call(
            sql.SQL("CREATE DATABASE {temp_db} TEMPLATE {DB_NAME};").format(
                temp_db=sql.Identifier(expected_temp_db),
                DB_NAME=sql.Identifier("db-name"),
            )
        )
        executed_sql = [str(c.args[0]) for c in mock_cursor.execute.call_args_list]
        assert (
            str(
                sql.SQL(
                    """
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'email';
        """
                )
            )
            in executed_sql
        )

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
            "--data-only",
            "--no-owner",
            "--no-privileges",
            "--format=custom",
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
        mock_cursor.execute.assert_any_call(
            sql.SQL("DROP DATABASE IF EXISTS {temp_db};").format(
                temp_db=sql.Identifier(expected_temp_db)
            )
        )
        mock_path.return_value.resolve.assert_called_once()
        mock_resolve.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_drop_db_fails_programming_error(self, mock_path, mock_connect, mock_run):
        """Test dump_data handles ProgrammingError when dropping temp DB."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("public.users",)]

        def side_effect_execute(query):
            if "DROP DATABASE" in str(query):
                msg = "Database does not exist"
                raise ProgrammingError(msg)

        mock_cursor.execute.side_effect = side_effect_execute

        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        call_command("dump_data", "--output", "data/dump.dump")

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_drop_db_fails_operational_error(self, mock_path, mock_connect, mock_run):
        """Test dump_data handles OperationalError when dropping temp DB."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("public.users",)]

        def side_effect_execute(query):
            if "DROP DATABASE" in str(query):
                msg = "Cannot connect to database"
                raise OperationalError(msg)

        mock_cursor.execute.side_effect = side_effect_execute

        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        call_command("dump_data", "--output", "data/dump.dump")

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_called_process_error(self, mock_path, mock_connect, mock_run):
        """Test dump_data handles CalledProcessError from pg_dump."""
        from subprocess import CalledProcessError

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("public.users",)]

        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Make run() raise CalledProcessError
        mock_run.side_effect = CalledProcessError(
            returncode=1, cmd=["pg_dump", "test"], output="pg_dump failed"
        )

        from django.core.management import CommandError

        with pytest.raises(CommandError) as exc_info:
            call_command("dump_data", "--output", "data/dump.dump")

        assert "Command failed:" in str(exc_info.value)
