#!/usr/bin/env bash
# Ensures the db-data Docker volume is not renamed across compose files.

set -euo pipefail

if grep -rn 'db-data[^:]' docker-compose/; then
  echo "" >&2
  echo "Error: The db volume must be 'db-data'." >&2
  exit 1
fi
