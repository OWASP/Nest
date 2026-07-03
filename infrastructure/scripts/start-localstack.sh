#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_FILE="$SCRIPT_DIR/../.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: $ENV_FILE not found." >&2
    echo "Create it with: LOCALSTACK_AUTH_TOKEN=<your-token>" >&2
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [[ -z "${LOCALSTACK_AUTH_TOKEN:-}" ]]; then
    echo "ERROR: LOCALSTACK_AUTH_TOKEN is not set in $ENV_FILE" >&2
    exit 1
fi

if ! command -v localstack >/dev/null 2>&1; then
    echo "ERROR: 'localstack' CLI not found. See infrastructure/README.md prerequisites." >&2
    exit 1
fi

echo "Starting LocalStack..."
exec localstack start
