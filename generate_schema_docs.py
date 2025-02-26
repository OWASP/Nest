from pathlib import Path
import subprocess


def generate_schema_docs():
    INPUT_DIR = Path("./schema")
    OUTPUT_DIR = Path("./docs/schema")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for schema_file in INPUT_DIR.iterdir():
        if (
            schema_file.suffix == ".json" and schema_file.name != "common.json"
        ):  # Exclude common.json
            base_name = schema_file.stem
            output_file = OUTPUT_DIR / f"{base_name}.md"

            print(f"Processing {schema_file} -> {output_file}")

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
