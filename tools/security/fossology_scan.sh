#!/bin/bash
# Copy the NUL-separated paths read from stdin out of the repository and run the FOSSology
# license scanners on the copy. Paths missing from the working tree (deleted locally) are
# skipped. Any other copy error fails the check before the scanner runs.
set -euo pipefail

repository_root="$1"
allowlist="$repository_root/.fossology-allowlist.json"
scanner="${FOSSOLOGY_SCANNER:-/bin/fossologyscanner}"

if [[ ! -f "$allowlist" ]]; then
    echo "Missing .fossology-allowlist.json" >&2
    exit 1
fi

scan_root="$(mktemp -d)"
while IFS= read -r -d '' path; do
    if [[ -e "$repository_root/$path" || -L "$repository_root/$path" ]]; then
        printf '%s\0' "$path"
    fi
done | tar -C "$repository_root" --null --files-from=- --create | tar -C "$scan_root" --extract

cd "$scan_root"
"$scanner" nomos ojo repo --allowlist-path "$allowlist"
