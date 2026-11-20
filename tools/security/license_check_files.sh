#!/usr/bin/env bash
set -euo pipefail

# Scan only files git tracks or would track, so .git, node_modules and caches are skipped.
# Files deleted from the working tree are dropped here; any other copy error fails the check.
git ls-files -z --cached --others --exclude-standard \
	| while IFS= read -r -d '' path; do
		if [[ ( -f "$path" || -L "$path" ) && ! -d "$path" ]]; then
			printf '%s\0' "$path"
		fi
	done
