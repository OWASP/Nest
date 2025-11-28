"""Dump masked data from the database into a compressed file."""

import os
from pathlib import Path
from subprocess import CalledProcessError, run

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


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
            default=["public.owasp_*", "public.github_*", "public.slack_*"],
            help=(
                "Table pattern to include. "
                "Defaults: public.owasp_*, public.github_*, public.slack_*"
            ),
        )

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        name = db.get("NAME", "")
        user = db.get("USER", "")
        password = db.get("PASSWORD", "")
        host = db.get("HOST", "localhost")
        port = str(db.get("PORT", "5432"))
        output_path = Path(options["output"]).resolve()
        tables = options["tables"] or []
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_db = f"temp_{name}"
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password

        self.stdout.write(self.style.NOTICE(f"Creating temporary database: {temp_db}"))
        try:
            # 1) Create temp DB from template
            self._psql(
                host,
                port,
                user,
                "postgres",
                f"CREATE DATABASE {temp_db} TEMPLATE {name};",
                env,
            )

            # 2) Hide emails
            self.stdout.write(self.style.NOTICE("Hiding email fields in temp DB…"))
            self._psql(host, port, user, temp_db, self._hide_emails(), env, via_stdin=True)

            # 3) Dump selected tables
            self.stdout.write(self.style.NOTICE(f"Creating dump at: {output_path}"))
            dump_cmd = [
                "pg_dump",
                "-h",
                host,
                "-p",
                port,
                "-U",
                user,
                "-d",
                temp_db,
                "--compress=9",
                "--clean",
            ]
            dump_cmd += [f"--table={table}" for table in tables]
            dump_cmd += ["-f", str(output_path)]

            run(dump_cmd, check=False, env=env)
            self.stdout.write(self.style.SUCCESS(f"Dump created: {output_path}"))
        except CalledProcessError as e:
            message = f"Command failed: {e.cmd}"
            raise CommandError(message) from e
        finally:
            # 4) Drop temp DB
            self.stdout.write(self.style.NOTICE(f"Dropping temporary database: {temp_db}"))
            try:
                self._psql(
                    host,
                    port,
                    user,
                    "postgres",
                    f"DROP DATABASE IF EXISTS {temp_db};",
                    env,
                )
            except CalledProcessError:
                # Best-effort cleanup
                self.stderr.write(
                    self.style.WARNING(f"Failed to drop temp DB {temp_db} (ignored).")
                )

    def _hide_emails(self) -> str:
        # Uses a DO block to UPDATE every column named 'email' in non-system schemas
        return """
DO $$
DECLARE
    record RECORD;
    statement TEXT;
BEGIN
    FOR record IN
        SELECT quote_ident(n.nspname) AS schemaname,
               quote_ident(c.relname) AS tablename,
               quote_ident(a.attname) AS colname
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE a.attname = 'email'
          AND a.attnum > 0
          AND NOT a.attisdropped
          AND n.nspname NOT IN ('pg_catalog','information_schema','pg_toast')
    LOOP
        statement := format(
            'UPDATE %s.%s SET %s = %L;', record.schemaname, record.tablename, record.colname, ''
        );
        EXECUTE statement;
    END LOOP;
END$$;
""".strip()

    def _psql(
        self,
        host: str,
        port: str,
        user: str,
        dbname: str,
        sql: str,
        env: dict,
        *,
        via_stdin: bool = False,
    ):
        # Inputs are trusted; safe subprocess usage.
        if via_stdin:
            run(
                ["psql", "-h", host, "-p", port, "-U", user, "-d", dbname],
                input=sql.encode(),
                check=True,
                env=env,
            )
            return
        run(
            ["psql", "-h", host, "-p", port, "-U", user, "-d", dbname, "-c", sql],
            check=True,
            env=env,
        )
