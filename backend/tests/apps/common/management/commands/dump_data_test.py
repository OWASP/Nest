from unittest.mock import MagicMock, patch

import pytest
from django.core.management import CommandError, call_command
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
    @patch("apps.common.management.commands.dump_data.Popen")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data(self, mock_path, mock_connect, mock_popen, mock_run):
        # Mock psycopg2 connection/cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        # Return table list for _table_list_query
        mock_cursor.fetchall.return_value = [("users",), ("members",)]
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Mock Popen for pg_dump and psql processes
        mock_dump_process = MagicMock()
        mock_dump_process.stdout = MagicMock()
        mock_dump_process.returncode = 0

        mock_psql_process = MagicMock()
        mock_psql_process.returncode = 0

        mock_popen.side_effect = [mock_dump_process, mock_psql_process]

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

        # Verify Popen was called twice (pg_dump and psql)
        assert mock_popen.call_count == 2

        # First Popen call: pg_dump
        first_popen_call = mock_popen.call_args_list[0]
        assert first_popen_call[0][0] == [
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

        # Second Popen call: psql
        second_popen_call = mock_popen.call_args_list[1]
        assert second_popen_call[0][0] == [
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
        assert second_popen_call[1]["stdin"] == mock_dump_process.stdout

        # Verify dump_process.stdout.close() was called
        mock_dump_process.stdout.close.assert_called_once()

        # Verify psql_process.communicate() was called
        mock_psql_process.communicate.assert_called_once()

        # Verify dump_process.wait() was called
        mock_dump_process.wait.assert_called_once()

        # Verify run was called once for final dump
        assert mock_run.call_count == 1

        # Verify final pg_dump call with table filters
        run_call = mock_run.call_args_list[0]
        assert run_call[0][0] == [
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
    @patch("apps.common.management.commands.dump_data.Popen")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_with_custom_tables(self, mock_path, mock_connect, mock_popen, mock_run):
        """Test dump_data with custom table arguments."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Mock Popen for pg_dump and psql processes
        mock_dump_process = MagicMock()
        mock_dump_process.stdout = MagicMock()
        mock_dump_process.returncode = 0

        mock_psql_process = MagicMock()
        mock_psql_process.returncode = 0

        mock_popen.side_effect = [mock_dump_process, mock_psql_process]

        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
            "--table",
            "public.custom_table",
        )

        # Verify the final pg_dump includes custom tables plus defaults
        run_call = mock_run.call_args_list[0]
        cmd_args = run_call[0][0]

        # Default tables should be present
        assert "--table=public.owasp_*" in cmd_args
        assert "--table=public.github_*" in cmd_args
        # Custom table should also be present
        assert "--table=public.custom_table" in cmd_args

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.Popen")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_no_email_tables(self, mock_path, mock_connect, mock_popen, mock_run):
        """Test dump_data when no tables have email columns."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        # No tables with email column
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Mock Popen for pg_dump and psql processes
        mock_dump_process = MagicMock()
        mock_dump_process.stdout = MagicMock()
        mock_dump_process.returncode = 0

        mock_psql_process = MagicMock()
        mock_psql_process.returncode = 0

        mock_popen.side_effect = [mock_dump_process, mock_psql_process]

        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
        )

        # Should still complete successfully
        assert mock_run.call_count == 1

        # No UPDATE email queries should be in executed SQL
        executed_sql = [str(c.args[0]) for c in mock_cursor.execute.call_args_list]
        update_queries = [q for q in executed_sql if "UPDATE" in q and "email" in q]
        assert len(update_queries) == 0

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.Popen")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_autocommit_enabled(self, mock_path, mock_connect, mock_popen, mock_run):
        """Test that autocommit is enabled on connections."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Mock Popen for pg_dump and psql processes
        mock_dump_process = MagicMock()
        mock_dump_process.stdout = MagicMock()
        mock_dump_process.returncode = 0

        mock_psql_process = MagicMock()
        mock_psql_process.returncode = 0

        mock_popen.side_effect = [mock_dump_process, mock_psql_process]

        call_command(
            "dump_data",
            "--output",
            "data/dump.dump",
        )

        # Verify autocommit was set to True on all connections
        assert mock_conn.autocommit is True
        # Verify connections were closed
        assert mock_conn.close.call_count >= 1

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.Popen")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_pg_dump_failure(self, mock_path, mock_connect, mock_popen, mock_run):
        """Test dump_data handles pg_dump failure correctly."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Mock Popen for pg_dump with failure
        mock_dump_process = MagicMock()
        mock_dump_process.stdout = MagicMock()
        mock_dump_process.returncode = 1  # Failure

        mock_psql_process = MagicMock()
        mock_psql_process.returncode = 0

        mock_popen.side_effect = [mock_dump_process, mock_psql_process]

        with pytest.raises(CommandError):
            call_command(
                "dump_data",
                "--output",
                "data/dump.dump",
            )

        # Verify dump_process.wait() was called before checking returncode
        mock_dump_process.wait.assert_called_once()

    @override_settings(DATABASES=DATABASES)
    @patch("apps.common.management.commands.dump_data.run")
    @patch("apps.common.management.commands.dump_data.Popen")
    @patch("apps.common.management.commands.dump_data.connect")
    @patch("apps.common.management.commands.dump_data.Path")
    def test_dump_data_psql_failure(self, mock_path, mock_connect, mock_popen, mock_run):
        """Test dump_data handles psql failure correctly."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_resolve = MagicMock()
        mock_path.return_value.resolve.return_value = mock_resolve

        # Mock Popen for pg_dump success but psql failure
        mock_dump_process = MagicMock()
        mock_dump_process.stdout = MagicMock()
        mock_dump_process.returncode = 0

        mock_psql_process = MagicMock()
        mock_psql_process.returncode = 1  # Failure

        mock_popen.side_effect = [mock_dump_process, mock_psql_process]

        with pytest.raises(CommandError):
            call_command(
                "dump_data",
                "--output",
                "data/dump.dump",
            )
