from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import override_settings
from psycopg2 import sql

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
        # Return table list for _table_list_query
        mock_cursor.fetchall.return_value = [("users",), ("members",)]
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Mock pg_dump output for data sync
        mock_pg_dump_result = MagicMock()
        mock_pg_dump_result.stdout = b"-- SQL dump data"
        mock_run.return_value = mock_pg_dump_result

        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
        )

        # Verify temp DB created
        expected_temp_db = "temp_db-name"

        # Verify connections were made
        mock_connect.assert_any_call(
            dbname="postgres",
            user="db-user",
            # ruff: noqa: S106
            password="db-pass",  # NOSONAR
            host="db-host",
            port="5432",
        )
        mock_connect.assert_any_call(
            dbname=expected_temp_db,
            user="db-user",
            password="db-pass",  # NOSONAR
            host="db-host",
            port="5432",
        )

        # Verify CREATE DATABASE was executed
        executed_sql = [str(c.args[0]) for c in mock_cursor.execute.call_args_list]
        assert (
            str(
                sql.SQL("CREATE DATABASE {temp_db}").format(
                    temp_db=sql.Identifier(expected_temp_db),
                )
            )
            in executed_sql
        )

        # Verify table list query was executed
        assert (
            str(
                sql.SQL("""
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'email';
        """)
            )
            in executed_sql
        )

        # Verify email removal queries were executed
        assert (
            str(sql.SQL("UPDATE {table} SET email = '';").format(table=sql.Identifier("users")))
            in executed_sql
        )
        assert (
            str(sql.SQL("UPDATE {table} SET email = '';").format(table=sql.Identifier("members")))
            in executed_sql
        )

        # Verify run calls - should be 3: pg_dump (data), psql (restore), pg_dump (final dump)
        assert mock_run.call_count == 3

        # First call: pg_dump to get data from original DB
        first_run_call = mock_run.call_args_list[0]
        assert first_run_call[0][0] == [
            "pg_dump",
            "-h",
            "db-host",
            "-p",
            "5432",
            "-U",
            "db-user",
            "-d",
            "db-name",
        ]
        assert first_run_call[1]["check"] is True
        assert first_run_call[1]["capture_output"] is True

        # Second call: psql to restore data to temp DB
        second_run_call = mock_run.call_args_list[1]
        assert second_run_call[0][0] == [
            "psql",
            "-h",
            "db-host",
            "-p",
            "5432",
            "-U",
            "db-user",
            "-d",
            expected_temp_db,
        ]
        assert second_run_call[1]["check"] is True
        assert second_run_call[1]["input"] == mock_pg_dump_result.stdout

        # Third call: pg_dump for final dump with table filters
        third_run_call = mock_run.call_args_list[2]
        assert third_run_call[0][0] == [
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
        ]

        # Ensure DROP DATABASE executed at the end
        assert (
            str(
                sql.SQL("DROP DATABASE IF EXISTS {temp_db};").format(
                    temp_db=sql.Identifier(expected_temp_db)
                )
            )
            in executed_sql
        )

        mock_path.return_value.resolve.assert_called_once()
        mock_resolve.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_with_custom_tables(self, mock_path, mock_connect, mock_run):
        """Test dump_data with custom table arguments."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        mock_pg_dump_result = MagicMock()
        mock_pg_dump_result.stdout = b"-- SQL dump data"
        mock_run.return_value = mock_pg_dump_result

        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
            "--table",
            "public.custom_table",
        )

        # Verify the final pg_dump includes custom tables plus defaults
        third_run_call = mock_run.call_args_list[2]
        cmd_args = third_run_call[0][0]

        # Default tables should be present
        assert "--table=public.owasp_*" in cmd_args
        assert "--table=public.github_*" in cmd_args
        # Custom table should also be present
        assert "--table=public.custom_table" in cmd_args

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_no_email_tables(self, mock_path, mock_connect, mock_run):
        """Test dump_data when no tables have email columns."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        # No tables with email column
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        mock_pg_dump_result = MagicMock()
        mock_pg_dump_result.stdout = b"-- SQL dump data"
        mock_run.return_value = mock_pg_dump_result

        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
        )

        # Should still complete successfully
        assert mock_run.call_count == 3

        # No UPDATE email queries should be in executed SQL
        executed_sql = [str(c.args[0]) for c in mock_cursor.execute.call_args_list]
        update_queries = [q for q in executed_sql if "UPDATE" in q and "email" in q]
        assert len(update_queries) == 0

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_autocommit_enabled(self, mock_path, mock_connect, mock_run):
        """Test that autocommit is enabled on connections."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        mock_pg_dump_result = MagicMock()
        mock_pg_dump_result.stdout = b"-- SQL dump data"
        mock_run.return_value = mock_pg_dump_result

        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
        )

        # Verify autocommit was set to True on all connections
        assert mock_conn.autocommit is True
        # Verify connections were closed
        assert mock_conn.close.call_count >= 1
