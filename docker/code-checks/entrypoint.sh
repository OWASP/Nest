#!/bin/sh
set -eu

# pre-commit refuses to run in a repo owned by a different UID (bind mounts).
git config --global --add safe.directory /nest

exec "$@"
