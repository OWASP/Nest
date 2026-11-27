#!/bin/bash -eu

export PYTHONPATH="${SRC}${PYTHONPATH:+:${PYTHONPATH}}"

compile_python_fuzzer "$SRC/tests/cluster-fuzz-lite/apps/slack/common/text.py"
compile_python_fuzzer "$SRC/tests/cluster-fuzz-lite/apps/common/search/query_parser.py"

sanitizer_lib_dir="$(python3 -c "import atheris; print(atheris.path())")"
case "${SANITIZER:-address}" in
  address)
    cp "${sanitizer_lib_dir}/asan_with_fuzzer.so" "$OUT/sanitizer_with_fuzzer.so"
    ;;
  undefined)
    cp "${sanitizer_lib_dir}/ubsan_with_fuzzer.so" "$OUT/sanitizer_with_fuzzer.so"
    ;;
  coverage | introspector)
    # Python coverage and introspector builds do not preload a sanitizer library.
    ;;
  *)
    echo "Unsupported SANITIZER for Python fuzzing: ${SANITIZER}" >&2
    exit 1
    ;;
esac
cp "$(command -v llvm-symbolizer)" "$OUT/llvm-symbolizer"

# Seeds are stored as loose files in .clusterfuzzlite/seed_corpora/ for review in git.
# ClusterFuzzLite expects {target}_seed_corpus.zip artifacts in $OUT at build time.
if compgen -G "$SRC/seed_corpora/apps/slack/common/text/*" > /dev/null; then
  zip -j "$OUT/text_seed_corpus.zip" "$SRC/seed_corpora/apps/slack/common/text/"*
fi

if compgen -G "$SRC/seed_corpora/apps/common/search/query_parser/*" > /dev/null; then
  zip -j "$OUT/query_parser_seed_corpus.zip" "$SRC/seed_corpora/apps/common/search/query_parser/"*
fi
