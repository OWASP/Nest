#!/bin/sh
set -eu

exit_code=0
for directory in . cspell e2e frontend; do
    printf '\nScanning %s with CVE Lite...\n' "$directory"
    status=0
    cve-lite "$directory" \
        --all \
        --verbose \
        --fail-on medium \
        --incomplete-policy error \
        --cache-dir .cache/cve-lite || status=$?
    if [ "$status" -gt "$exit_code" ]; then
        exit_code=$status
    fi
done

exit "$exit_code"
