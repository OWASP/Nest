#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: $0 <environment> <enable-additional-parameters>" >&2
  exit 1
}

[[ $# -eq 2 ]] || usage

environment=$1
enable_additional_parameters=$2

if [[ "$enable_additional_parameters" != "true" && "$enable_additional_parameters" != "false" ]]; then
  usage
fi

check_secret() {
  local secret_id=$1

  # Check version metadata without retrieving or printing the secret value.
  if ! aws secretsmanager describe-secret \
    --secret-id "$secret_id" \
    --query 'VersionIdsToStages' \
    --output json | jq -e 'any(.[]; index("AWSCURRENT") != null)' >/dev/null; then
    echo "::error::Secret has no AWSCURRENT version: ${secret_id}" >&2
    exit 1
  fi
}

secret_names=(
  DJANGO_ALGOLIA_WRITE_API_KEY
  DJANGO_OPEN_AI_SECRET_KEY
  DJANGO_REDIS_PASSWORD
  DJANGO_SECRET_KEY
  DJANGO_SENTRY_DSN
  DJANGO_SLACK_BOT_TOKEN
  DJANGO_SLACK_SIGNING_SECRET
  GITHUB_TOKEN
  NEXTAUTH_SECRET
  NEXT_SERVER_GITHUB_CLIENT_SECRET
)

if [[ "$enable_additional_parameters" == "true" ]]; then
  secret_names+=(NEST_GITHUB_APP_PRIVATE_KEY SLACK_BOT_TOKEN_T04T40NHX)
fi

for secret_name in "${secret_names[@]}"; do
  check_secret "/nest/${environment}/${secret_name}"
done

check_secret "nest-${environment}-db-credentials"

echo "All required runtime secrets have an AWSCURRENT version."
