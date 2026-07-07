#!/usr/bin/env bash

set -euo pipefail

# --- Config -------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

LOCALSTACK_CONTAINER_NAME="localstack"
LOCALSTACK_IMAGE="$(grep -E '^FROM localstack/localstack(-pro)?:' "$ROOT_DIR/docker/localstack/Dockerfile" | sed 's/^FROM //')"
if [[ -z "$LOCALSTACK_IMAGE" ]]; then
    echo "Error: could not determine LocalStack image from docker/localstack/Dockerfile." >&2
    exit 1
fi
LOCALSTACK_HEALTH_URL="http://localhost:4566/_localstack/info"
HEALTH_MAX_ATTEMPTS=30
HEALTH_POLL_INTERVAL=2

# S3 bucket override files, used to disable prevent_destroy during tests.
# Format: "file_path:resource_type.resource_name"
OVERRIDES=(
    "infrastructure/modules/storage/modules/s3-bucket/test_override.tf:aws_s3_bucket.this"
    "infrastructure/modules/storage/modules/shared-data-bucket/test_override.tf:aws_s3_bucket.nest_shared_data"
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
    local item file resource resource_name local_name
    for item in "${OVERRIDES[@]}"; do
        file="${item%%:*}"
        resource="${item#*:}"
        local_name="${resource#*.}"
        resource_name="${resource%%.*}"
        printf 'resource "%s" "%s" {\n  lifecycle {\n    prevent_destroy = false\n  }\n}\n' \
            "$resource_name" "$local_name" > "$file"
    done
}

cleanup() {
    echo "Cleaning up override files..."
    local item file
    for item in "${OVERRIDES[@]}"; do
        file="${item%%:*}"
        rm -f "$file"
    done

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

    echo "Waiting for LocalStack license activation..."
    local license_attempt=1
    local license_max_attempts=15
    while ! curl -sf --connect-timeout 2 "$LOCALSTACK_HEALTH_URL" 2>/dev/null \
            | grep -q '"is_license_activated": *true'; do
        if [[ "$license_attempt" -ge "$license_max_attempts" ]]; then
            echo "Error: LocalStack license failed to activate within $((license_max_attempts * HEALTH_POLL_INTERVAL)) seconds." >&2
            docker logs "$LOCALSTACK_CONTAINER_NAME" 2>&1 | tail -30
            exit 1
        fi
        sleep "$HEALTH_POLL_INTERVAL"
        license_attempt=$((license_attempt + 1))
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

for item in "${OVERRIDES[@]}"; do
    file="${item%%:*}"
    if [[ -f "$file" ]]; then
        echo "Error: $file already exists. Refusing to run to avoid overwriting." >&2
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
