#!/bin/bash -eu

python -m pip install \
    atheris==3.0.0 \
    pyparsing==3.3.2

cp "$SRC/Nest/backend/tests/fuzz/fuzz_query_parser_test.py" \
   "$OUT/fuzz_query_parser_test.py"

cat > "$OUT/fuzz_query_parser" <<'RUNNER'
#!/bin/bash

cd "$(dirname "$0")"

PYTHONPATH=/src/Nest/backend \
exec python fuzz_query_parser_test.py "$@"
RUNNER

chmod +x "$OUT/fuzz_query_parser"
