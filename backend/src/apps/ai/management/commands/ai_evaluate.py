"""Evaluate RAG agents or assistant flows against fixed retrieval fixtures."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.ai.evaluation.datasets.rag_fixtures import RAG_FIXTURES
from apps.ai.evaluation.flow_runner import run_flow_case
from apps.ai.evaluation.rag_runner import run_rag_case


class Command(BaseCommand):
    help = "Evaluate RAG-agent or assistant-flow responses using fixed retrieval fixtures."
    requires_system_checks: list[str] = []

    def add_arguments(self, parser):
        parser.add_argument("--live", action="store_true")
        parser.add_argument(
            "--case-id",
            choices=tuple(RAG_FIXTURES),
            default="rag-002",
        )
        parser.add_argument(
            "--scenario",
            choices=("relevant", "irrelevant", "empty", "mixed", "all"),
            default="relevant",
        )
        parser.add_argument("--output", help="Optional JSON report path.")

        parser.add_argument(
            "--scope",
            choices=("rag_agent", "assistant_flow"),
            default="rag_agent",
        )

    def handle(self, *args, **options):
        if not options["live"]:
            msg = "Use --live to enable LLM evaluations."
            raise CommandError(msg)

        output_path = Path(options["output"]) if options["output"] else None
        if output_path is not None and (output_path.is_dir() or not output_path.parent.is_dir()):
            msg = "Output must be a file path inside an existing directory."
            raise CommandError(msg)

        case_id = options["case_id"]
        scenarios = (
            list(RAG_FIXTURES[case_id]) if options["scenario"] == "all" else [options["scenario"]]
        )

        scope = options["scope"]
        runner = run_flow_case if scope == "assistant_flow" else run_rag_case

        results = []
        for scenario in scenarios:
            try:
                result = runner(case_id, scenario, live=True)
            except Exception as error:  # noqa: BLE001 - preserve failures and continue
                result = {
                    "scope": scope,
                    "case_id": case_id,
                    "scenario": scenario,
                    "status": "failed",
                    "error": f"{type(error).__name__}: {error}",
                }
            results.append(result)

        summary = {"total": len(results)}
        for status in ("passed", "failed", "needs_review"):
            summary[status] = sum(result["status"] == status for result in results)

        report = {
            "scope": scope,
            "summary": summary,
            "results": results,
        }
        serialized = json.dumps(report, indent=2, ensure_ascii=False)
        self.stdout.write(serialized)

        if output_path is not None:
            try:
                output_path.write_text(serialized + "\n", encoding="utf-8")
            except OSError as error:
                msg = f"Could not write report: {error}"
                raise CommandError(msg) from error

        if summary["failed"]:
            msg = f"{summary['failed']} evaluation run(s) failed."
            raise CommandError(msg)

        if summary["needs_review"]:
            msg = f"{summary['needs_review']} evaluation run(s) require review."
            raise CommandError(msg, returncode=2)
