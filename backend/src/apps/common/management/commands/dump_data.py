"""Dump masked data from the database into a compressed file."""

import contextlib
import os
from pathlib import Path
from subprocess import PIPE, CalledProcessError, Popen, run

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from psycopg2 import OperationalError, ProgrammingError, connect, sql

DEFAULT_DATABASE = settings.DATABASES["default"]
DB_HOST = DEFAULT_DATABASE.get("HOST", "localhost")
DB_PORT = str(DEFAULT_DATABASE.get("PORT", "5432"))
DB_USER = DEFAULT_DATABASE.get("USER", "")
DB_PASSWORD = DEFAULT_DATABASE.get("PASSWORD", "")
DB_NAME = DEFAULT_DATABASE.get("NAME", "")

PG_DUMP = "/usr/bin/pg_dump"
PSQL = "/usr/bin/psql"


class Command(BaseCommand):
    help = "Create a dump of selected db tables."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=str(Path(settings.BASE_DIR) / "data" / "nest.dump"),
            help="Output dump path (default: data/nest.dump)",
        )
        parser.add_argument(
            "-t",
            "--table",
            action="append",
            dest="tables",
            default=[
                "public.owasp_*",
                "public.github_*",
                "public.slack_members",
                "public.slack_workspaces",
                "public.slack_conversations",
                "public.slack_messages",
            ],
            help="Table pattern to include",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"]).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tables = options["tables"] or []

        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD

        temp_db = f"temp_{DB_NAME}"
        try:
            self._execute_sql(
                "postgres",
                [sql.SQL("CREATE DATABASE {temp_db}").format(temp_db=sql.Identifier(temp_db))],
            )

            self.stdout.write(self.style.SUCCESS(f"Created temporary DB: {temp_db}"))

            # Getting data.
            dump_process = Popen(  # noqa: S603
                [
                    PG_DUMP,
                    "-h",
                    DB_HOST,
                    "-p",
                    DB_PORT,
                    "-U",
                    DB_USER,
                    "-d",
                    DB_NAME,
                ],
                stdout=PIPE,
                env=env,
            )
            psql_process = Popen(  # noqa: S603
                [
                    PSQL,
                    "-h",
                    DB_HOST,
                    "-p",
                    DB_PORT,
                    "-U",
                    DB_USER,
                    "-d",
                    temp_db,
                ],
                env=env,
                stdin=dump_process.stdout,
            )

            dump_process.stdout.close()
            psql_process.communicate()
            dump_process.wait()
            if dump_process.returncode or psql_process.returncode:
                message = f"Failed to sync data from {DB_NAME} to {temp_db}"
                raise CommandError(message)

            self.stdout.write(self.style.SUCCESS(f"Synced data from {DB_NAME} to {temp_db}"))
            table_list = self._execute_sql(temp_db, [self._table_list_query()])
            self._execute_sql(temp_db, self._remove_emails([row[0] for row in table_list]))
            self.stdout.write(self.style.SUCCESS("Removed emails from temporary DB"))

            dump_cmd = [
                PG_DUMP,
                "-h",
                DB_HOST,
                "-p",
                DB_PORT,
                "-U",
                DB_USER,
                "-d",
                temp_db,
                "--compress=9",
                "--data-only",
                "--no-owner",
                "--no-privileges",
                "--format=custom",
            ]
            dump_cmd += [f"--table={table}" for table in tables]
            dump_cmd += ["-f", str(output_path)]

            run(dump_cmd, check=True, env=env)  # noqa: S603
            self.stdout.write(self.style.SUCCESS(f"Created dump: {output_path}"))
        except CalledProcessError as e:
            message = f"Command failed: {e.cmd}"
            raise CommandError(message) from e
        finally:
            try:
                self._execute_sql(
                    "postgres",
                    [
                        sql.SQL("DROP DATABASE IF EXISTS {temp_db};").format(
                            temp_db=sql.Identifier(temp_db)
                        )
                    ],
                )
            except (ProgrammingError, OperationalError):
                self.stderr.write(
                    self.style.WARNING(f"Failed to drop temp DB {temp_db} (ignored).")
                )

    def _table_list_query(self) -> sql.Composable:
        return sql.SQL("""
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'email';
        """)

    def _remove_emails(self, tables: list[str]) -> list[sql.Composable]:
        return [
            sql.SQL("UPDATE {table} SET email = '';").format(table=sql.Identifier(table))
            for table in tables
        ]

    def _execute_sql(
        self,
        dbname: str,
        sql_queries: list[sql.Composable],
    ):
        connection = connect(
            dbname=dbname,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        connection.autocommit = True

        rows = []
        with connection.cursor() as cursor:
            for sql_query in sql_queries:
                cursor.execute(sql_query)
                with contextlib.suppress(ProgrammingError):
                    rows.extend(cursor.fetchall())
        connection.close()

        return rows
