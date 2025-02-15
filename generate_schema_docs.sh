# generate_each_schema_doc.sh

INPUT_DIR="./schema"
OUTPUT_DIR="./docs/schema"

mkdir -p "$OUTPUT_DIR"

for schema in "$INPUT_DIR"/*.json; do
  base=$(basename "$schema" .json)
  echo "Processing $schema -> $OUTPUT_DIR/$base.md"
  generate-schema-doc --config template_name=md "$schema" "$OUTPUT_DIR/$base.md"
done

# Post-process: Remove the auto-generated header line from each Markdown file
for mdfile in "$OUTPUT_DIR"/*.md; do
  sed -i '' '/^Generated using/d' "$mdfile"
done
