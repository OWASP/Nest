#!/usr/bin/env bash

set -euo pipefail

# --- Config -------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

LOCALSTACK_CONTAINER_NAME="localstack"
LOCALSTACK_IMAGE="$(grep -E '^FROM localstack/localstack:' "$ROOT_DIR/docker/localstack/Dockerfile" | sed 's/^FROM //')"
LOCALSTACK_HEALTH_URL="http://localhost:4566/_localstack/health"
HEALTH_MAX_ATTEMPTS=30
HEALTH_POLL_INTERVAL=2

# S3 bucket override files, used to disable prevent_destroy during tests.
OVERRIDE_FILES=(
    "infrastructure/modules/storage/modules/s3-bucket/test_override.tf"
    "infrastructure/modules/storage/modules/shared-data-bucket/test_override.tf"
)
OVERRIDE_RESOURCES=(
    "aws_s3_bucket.this"
    "aws_s3_bucket.nest_shared_data"
)

LOCALSTACK_STARTED=false

# --- Helpers --------------------------------------------------------------

require_cmd() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || {
        echo "Error: required command '$cmd' not found on PATH." >&2
        exit 1
    }
}

localstack_healthy() {
    curl -sf --connect-timeout 2 "$LOCALSTACK_HEALTH_URL" >/dev/null 2>&1
}

write_override_files() {
    local i resource_name local_name
    for i in "${!OVERRIDE_FILES[@]}"; do
        local_name="${OVERRIDE_RESOURCES[$i]#*.}"
        resource_name="${OVERRIDE_RESOURCES[$i]%%.*}"
        printf 'resource "%s" "%s" {\n  lifecycle {\n    prevent_destroy = false\n  }\n}\n' \
            "$resource_name" "$local_name" > "${OVERRIDE_FILES[$i]}"
    done
}

cleanup() {
    echo "Cleaning up override files..."
    rm -f "${OVERRIDE_FILES[@]}"

    if [[ "$LOCALSTACK_STARTED" == "true" ]]; then
        echo "Stopping and removing LocalStack container..."
        docker stop "$LOCALSTACK_CONTAINER_NAME" >/dev/null 2>&1 || true
        docker rm "$LOCALSTACK_CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
}

start_localstack() {
    if [[ -z "${LOCALSTACK_AUTH_TOKEN:-}" ]]; then
        echo "Error: LOCALSTACK_AUTH_TOKEN environment variable is not set." >&2
        echo "LocalStack integration tests require a valid auth token to run." >&2
        exit 1
    fi

    # In case a stale/stopped container from a previous failed run is lingering.
    docker rm -f "$LOCALSTACK_CONTAINER_NAME" >/dev/null 2>&1 || true

    echo "Starting LocalStack container..."
    docker run -d --name "$LOCALSTACK_CONTAINER_NAME" \
        -p 4566:4566 \
        -e LOCALSTACK_AUTH_TOKEN="$LOCALSTACK_AUTH_TOKEN" \
        "$LOCALSTACK_IMAGE" >/dev/null

    LOCALSTACK_STARTED=true

    echo "Waiting for LocalStack to become healthy..."
    local attempt=1
    while ! localstack_healthy; do
        if [[ "$attempt" -ge "$HEALTH_MAX_ATTEMPTS" ]]; then
            echo "Error: LocalStack failed to become healthy within $((HEALTH_MAX_ATTEMPTS * HEALTH_POLL_INTERVAL)) seconds." >&2
            exit 1
        fi
        echo "Waiting... (attempt $attempt/$HEALTH_MAX_ATTEMPTS)"
        sleep "$HEALTH_POLL_INTERVAL"
        attempt=$((attempt + 1))
    done
    echo "LocalStack is ready!"
}

run_module_tests() {
    local test_dir="$1"
    local module_dir
    module_dir="$(dirname "$test_dir")"

    local filters=()
    while IFS= read -r -d '' test_file; do
        filters+=("-filter=tests/$(basename "$test_file")")
    done < <(find "$test_dir" -maxdepth 1 -name "*integration*.tftest.hcl" -print0)

    [[ "${#filters[@]}" -eq 0 ]] && return 0

    echo "Testing integration for $module_dir..."
    terraform -chdir="$module_dir" init -backend=false -input=false || exit 1
    terraform -chdir="$module_dir" test "${filters[@]}" || exit 1
    
    test_count=$((test_count + 1))
    return 0
}

# --- Main -------------------------------------------------------------

require_cmd docker
require_cmd terraform
require_cmd curl

cd "$ROOT_DIR"

for f in "${OVERRIDE_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "Error: $f already exists. Refusing to run to avoid overwriting." >&2
        exit 1
    fi
done

trap cleanup EXIT

if localstack_healthy; then
    echo "Using already running LocalStack instance."
else
    echo "LocalStack is not running on port 4566. Attempting to start it..."
    start_localstack
fi

write_override_files

test_count=0
while IFS= read -r -d '' test_dir; do
    run_module_tests "$test_dir"
done < <(find infrastructure/bootstrap infrastructure/modules -name "tests" -type d -not -path "*/.terraform/*" -print0)

if [[ "$test_count" -eq 0 ]]; then
    echo "Error: No integration tests were found or executed." >&2
    exit 1
fi

echo "All integration tests executed successfully!"
