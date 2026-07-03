#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE not found."
    echo "Create it with: LOCALSTACK_AUTH_TOKEN=<your-token>"
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [ -z "${LOCALSTACK_AUTH_TOKEN:-}" ]; then
    echo "ERROR: LOCALSTACK_AUTH_TOKEN is not set in $ENV_FILE"
    exit 1
fi

echo "Starting LocalStack..."
exec localstack start
