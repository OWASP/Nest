#!/bin/sh
set -eu

exit_code=0
for directory in . cspell e2e frontend; do
    printf '\nScanning %s with CVE Lite CLI...\n' "$directory"
    status=0
    cve-lite "$directory" \
        --all \
        --cache-dir .cache/cve-lite \
        --fail-on medium \
        --incomplete-policy error \
        --verbose || status=$?
    if [ "$status" -gt "$exit_code" ]; then
        exit_code=$status
    fi
done

exit "$exit_code"
