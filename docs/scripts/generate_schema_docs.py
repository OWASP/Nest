"""Generate schema documentation from JSON schema files."""

# ruff: noqa: S603 https://docs.astral.sh/ruff/rules/subprocess-without-shell-equals-true/
# ruff: noqa: S607 https://docs.astral.sh/ruff/rules/start-process-with-partial-path/

import subprocess
from pathlib import Path


def generate_schema_docs():
    """Generate documentation from JSON schema files."""
    input_dir = Path("./schema")
    output_dir = Path("./docs/schema")

    output_dir.mkdir(parents=True, exist_ok=True)

    for schema_file in input_dir.iterdir():
        if schema_file.suffix == ".json" and schema_file.name != "common.json":
            base_name = schema_file.stem
            output_file = output_dir / f"{base_name}.md"

            # Generate the schema documentation
            subprocess.run(
                [
                    "generate-schema-doc",
                    "--config",
                    "template_name=md",
                    str(schema_file),
                    str(output_file),
                ],
                check=True,
            )

            # Post-process: Remove the auto-generated header line
            lines = output_file.read_text(encoding="utf-8").splitlines()
            filtered_lines = [line for line in lines if "Generated using" not in line]
            output_file.write_text("\n".join(filtered_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    generate_schema_docs()
