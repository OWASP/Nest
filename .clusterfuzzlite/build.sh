#!/bin/bash -eu

pip3 install -r "$SRC/Nest/backend/requirements/fuzz.txt"

cp -r "$SRC/Nest/backend/apps" "$SRC/apps"
cp "$SRC/Nest/backend/tests/fuzz/fuzz_nest_test.py" "$SRC/fuzz_nest_test.py"
cp "$SRC/Nest/backend/tests/fuzz/fuzz_query_parser_test.py" "$SRC/fuzz_query_parser_test.py"

compile_python_fuzzer "$SRC/fuzz_nest_test.py"
compile_python_fuzzer "$SRC/fuzz_query_parser_test.py"
