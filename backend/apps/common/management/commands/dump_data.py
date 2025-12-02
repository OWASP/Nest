"""Dump masked data from the database into a compressed file."""

import contextlib
import os
from pathlib import Path
from subprocess import CalledProcessError, run

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from psycopg2 import ProgrammingError, connect, sql

DB = settings.DATABASES["default"]
HOST = DB.get("HOST", "localhost")
PORT = str(DB.get("PORT", "5432"))
USERNAME = DB.get("USER", "")
PASSWORD = DB.get("PASSWORD", "")
NAME = DB.get("NAME", "")


class Command(BaseCommand):
    help = "Create a dump of selected db tables."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=str(Path(settings.BASE_DIR) / "data" / "nest.sql.gz"),
            help="Output dump path (default: data/nest.sql.gz)",
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
            help=(
                "Table pattern to include. "
                "Defaults: public.owasp_*, public.github_*, public.slack_members, "
                "public.slack_workspaces, public.slack_conversations, public.slack_messages."
            ),
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"]).resolve()
        tables = options["tables"] or []
        output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_db = f"temp_{NAME}"
        env = os.environ.copy()
        env["PGPASSWORD"] = PASSWORD
        self.stdout.write(self.style.NOTICE(f"Creating temporary database: {temp_db}"))
        try:
            # 1) Create temp DB from template
            self._execute_sql(
                "postgres",
                [f"CREATE DATABASE {temp_db} TEMPLATE {NAME};"],
            )
            # 2) Get tables with email field
            self.stdout.write(self.style.NOTICE("Fetching tables with email fields…"))

            table_list = self._execute_sql(
                temp_db,
                [self._table_list_query()],
            )

            # 3) Hide email fields
            self.stdout.write(self.style.NOTICE("Hiding email fields in temp DB…"))
            self._execute_sql(temp_db, self._hide_emails_queries([row[0] for row in table_list]))
            # 4) Dump selected tables
            self.stdout.write(self.style.NOTICE(f"Creating dump at: {output_path}"))
            dump_cmd = [
                "pg_dump",
                "-h",
                HOST,
                "-p",
                PORT,
                "-U",
                USERNAME,
                "-d",
                temp_db,
                "--compress=9",
                "--clean",
            ]
            dump_cmd += [f"--table={table}" for table in tables]
            dump_cmd += ["-f", str(output_path)]

            run(dump_cmd, check=True, env=env)
            self.stdout.write(self.style.SUCCESS(f"Dump created: {output_path}"))
        except CalledProcessError as e:
            message = f"Command failed: {e.cmd}"
            raise CommandError(message) from e
        finally:
            # 4) Drop temp DB
            self.stdout.write(self.style.NOTICE(f"Dropping temporary database: {temp_db}"))
            try:
                self._execute_sql(
                    "postgres",
                    [f"DROP DATABASE IF EXISTS {temp_db};"],
                )
            except CalledProcessError:
                # Best-effort cleanup
                self.stderr.write(
                    self.style.WARNING(f"Failed to drop temp DB {temp_db} (ignored).")
                )

    def _table_list_query(self) -> str:
        return """
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'email';
        """

    def _hide_emails_queries(self, tables: list[str]) -> list[str]:
        return [
            sql.SQL("UPDATE {table} SET email = '';").format(table=sql.Identifier(table))
            for table in tables
        ]

    def _execute_sql(
        self,
        dbname: str,
        sql_queries: list[str],
    ):
        connection = connect(
            dbname=dbname,
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            port=PORT,
        )
        connection.autocommit = True
        rows = []
        with connection.cursor() as cursor:
            for sql in sql_queries:
                cursor.execute(sql)
                with contextlib.suppress(ProgrammingError):
                    rows.extend(cursor.fetchall())
        connection.close()
        return rows
