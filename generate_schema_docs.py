import os
import subprocess

INPUT_DIR = "./schema"
OUTPUT_DIR = "./docs/schema"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for schema_file in os.listdir(INPUT_DIR):
    if schema_file.endswith(".json"):
        schema_path = os.path.join(INPUT_DIR, schema_file)
        base_name = os.path.splitext(schema_file)[0]
        output_file = os.path.join(OUTPUT_DIR, f"{base_name}.md")

        print(f"Processing {schema_path} -> {output_file}")

        # Generate the schema documentation
        subprocess.run(
            [
                "generate-schema-doc",
                "--config",
                "template_name=md",
                schema_path,
                output_file,
            ],
            check=True,
        )

        # Post-process: Remove the auto-generated header line
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(output_file, "w", encoding="utf-8") as f:
            for line in lines:
                if "Generated using" not in line:
                    f.write(line)
