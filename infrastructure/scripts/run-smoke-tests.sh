#!/usr/bin/env bash

set -euo pipefail

LOCALSTACK_HOST="${LOCALSTACK_HOST:-localhost}"
LOCALSTACK_PORT="${LOCALSTACK_PORT:-4566}"
LOCALSTACK_URL="http://${LOCALSTACK_HOST}:${LOCALSTACK_PORT}"
LOCALSTACK_IMAGE="localstack/localstack:2026.6.0"
LOCALSTACK_CONTAINER="localstack-smoke"

STARTED_CONTAINER=false

wait_for_localstack() {
  echo "Waiting for LocalStack to be ready..."
  for i in $(seq 1 30); do
    local health
    health=$(curl -sf "${LOCALSTACK_URL}/_localstack/health") || health=""
    if echo "${health}" | grep -q '"s3".*"available"' && \
       echo "${health}" | grep -q '"kms".*"available"' && \
       echo "${health}" | grep -q '"iam".*"available"' && \
       echo "${health}" | grep -q '"sts".*"available"'; then
      echo "LocalStack is ready."
      return 0
    fi
    sleep 2
  done
  echo "LocalStack did not become ready in time."
  exit 1
}

if curl -sf "${LOCALSTACK_URL}/_localstack/health" >/dev/null 2>&1; then
  echo "Found existing LocalStack instance at ${LOCALSTACK_URL}, verifying readiness..."
  wait_for_localstack
else
  echo "Starting LocalStack container..."
  docker run -d \
    --name "${LOCALSTACK_CONTAINER}" \
    -p "${LOCALSTACK_PORT}:4566" \
    -e LOCALSTACK_AUTH_TOKEN="${LOCALSTACK_AUTH_TOKEN:-}" \
    "${LOCALSTACK_IMAGE}"
  STARTED_CONTAINER=true
  trap 'override_s3_lifecycle remove; cleanup' EXIT
  wait_for_localstack
fi

cleanup() {
  if [[ "${STARTED_CONTAINER}" = "true" ]]; then
    echo "Stopping LocalStack container..."
    docker stop "${LOCALSTACK_CONTAINER}" >/dev/null 2>&1 || true
    docker rm "${LOCALSTACK_CONTAINER}" >/dev/null 2>&1 || true
  fi
}

override_s3_lifecycle() {
  local action="${1}"
  local s3_override="infrastructure/modules/storage/modules/s3-bucket/test_override.tf"
  local shared_override="infrastructure/modules/storage/modules/shared-data-bucket/test_override.tf"

  if [[ "${action}" = "create" ]]; then
    if [[ -f "${s3_override}" ]] || [[ -f "${shared_override}" ]]; then
      echo "Error: test_override.tf already exists. Refusing to overwrite." >&2
      exit 1
    fi
    printf 'resource "aws_s3_bucket" "this" {\n  lifecycle {\n    prevent_destroy = false\n  }\n}\n' > "${s3_override}"
    printf 'resource "aws_s3_bucket" "nest_shared_data" {\n  lifecycle {\n    prevent_destroy = false\n  }\n}\n' > "${shared_override}"
  elif [[ "${action}" = "remove" ]]; then
    rm -f "${s3_override}" "${shared_override}"
  fi
}

test_count=0
fail_count=0

run_smoke_tests() {
  local module_dir="${1}"
  local test_dir="${module_dir}/tests"
  local filters=""

  for test_file in "${test_dir}"/*.tftest.hcl; do
    [[ -e "${test_file}" ]] || continue
    filename=$(basename "${test_file}")
    # Match only *smoke* files — mirrors the exclusion pattern in infrastructure/Makefile
    case "${filename}" in
      *smoke*) filters="${filters} -filter=tests/${filename}" ;;
      *) ;;
    esac
  done

  [[ -n "${filters}" ]] || return 0

  echo "Running smoke tests for ${module_dir}..."
  terraform -chdir="${module_dir}" init -backend=false -input=false

  # shellcheck disable=SC2086
  if terraform -chdir="${module_dir}" test ${filters}; then
    test_count=$((test_count + 1))
  else
    fail_count=$((fail_count + 1))
  fi
}

override_s3_lifecycle create
trap 'override_s3_lifecycle remove; cleanup' EXIT

test_dirs=$(find infrastructure/bootstrap infrastructure/modules \
  -name "tests" -type d -not -path "*/.terraform/*" | sort)

while IFS= read -r test_dir; do
  run_smoke_tests "$(dirname "${test_dir}")"
done <<< "${test_dirs}"

echo ""
echo "Smoke test results: ${test_count} passed, ${fail_count} failed."

if [[ "${test_count}" -eq 0 ]]; then
  echo "Error: no smoke tests were executed."
  exit 1
fi

[[ "${fail_count}" -eq 0 ]] || exit 1
