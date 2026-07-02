#!/usr/bin/env bash

set -euo pipefail

repository_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
fixture_dir="${repository_root}/infrastructure/localstack"

export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-test}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-test}
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-2}
export AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL:-http://localhost:4566}

fail() {
  echo "LocalStack migration test failed: $*" >&2
  exit 1
}

for command in aws awslocal jq tflocal; do
  command -v "$command" >/dev/null || fail "required command not found: ${command}"
done

awslocal sts get-caller-identity >/dev/null || fail "LocalStack is not reachable"

cleanup() {
  echo "Destroying LocalStack runtime-secrets fixture..."
  tflocal -chdir="$fixture_dir" destroy \
    -auto-approve \
    -input=false \
    -var='runtime_secrets_mode=complete' >/dev/null || true
}
trap cleanup EXIT

secret_parameter_names=(
  DJANGO_ALGOLIA_WRITE_API_KEY
  DJANGO_DB_PASSWORD
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

external_secret_names=(
  DJANGO_ALGOLIA_WRITE_API_KEY
  DJANGO_OPEN_AI_SECRET_KEY
  DJANGO_SENTRY_DSN
  DJANGO_SLACK_BOT_TOKEN
  DJANGO_SLACK_SIGNING_SECRET
  GITHUB_TOKEN
  NEXT_SERVER_GITHUB_CLIENT_SECRET
)

assert_secret_has_current() {
  local secret_id=$1

  awslocal secretsmanager describe-secret \
    --secret-id "$secret_id" \
    --query 'VersionIdsToStages' \
    --output json |
    jq -e 'any(.[]; index("AWSCURRENT") != null)' >/dev/null ||
    fail "secret has no AWSCURRENT version: ${secret_id}"
}

echo "Initializing the focused Terraform fixture..."
tflocal -chdir="$fixture_dir" init -backend=false -input=false >/dev/null

echo "Applying prepare mode: SSM and Secrets Manager must coexist..."
tflocal -chdir="$fixture_dir" apply \
  -auto-approve \
  -input=false \
  -var='runtime_secrets_mode=prepare' >/dev/null

for name in "${secret_parameter_names[@]}"; do
  awslocal ssm get-parameter --name "/nest/localstack/${name}" >/dev/null ||
    fail "prepare mode did not retain SSM parameter: ${name}"
done

for name in "${external_secret_names[@]}"; do
  awslocal secretsmanager describe-secret --secret-id "/nest/localstack/${name}" >/dev/null ||
    fail "Secrets Manager container was not created: ${name}"
done

assert_secret_has_current "/nest/localstack/DJANGO_SECRET_KEY"
assert_secret_has_current "/nest/localstack/NEXTAUTH_SECRET"
assert_secret_has_current "/nest/localstack/DJANGO_REDIS_PASSWORD"
assert_secret_has_current "nest-localstack-db-credentials"

echo "Populating externally managed secrets with fake LocalStack values..."
for name in "${external_secret_names[@]}"; do
  awslocal secretsmanager put-secret-value \
    --secret-id "/nest/localstack/${name}" \
    --secret-string "fake-${name}" >/dev/null
done

echo "Running the same AWSCURRENT preflight used by deployment..."
AWS_ENDPOINT_URL="$AWS_ENDPOINT_URL" \
  "${repository_root}/.github/scripts/verify-runtime-secrets.sh" localstack false >/dev/null

echo "Applying complete mode: secret-valued SSM parameters must be removed..."
tflocal -chdir="$fixture_dir" apply \
  -auto-approve \
  -input=false \
  -var='runtime_secrets_mode=complete' >/dev/null

for name in "${secret_parameter_names[@]}"; do
  if awslocal ssm get-parameter --name "/nest/localstack/${name}" >/dev/null 2>&1; then
    fail "complete mode retained secret-valued SSM parameter: ${name}"
  fi
done

parameter_type=$(awslocal ssm get-parameter \
  --name /nest/localstack/DJANGO_ALLOWED_HOSTS \
  --query 'Parameter.Type' \
  --output text)
[[ "$parameter_type" == "String" ]] || fail "complete mode removed or changed a non-secret SSM parameter"

task_definition_arn=$(tflocal -chdir="$fixture_dir" output -raw task_definition_arn)
ecs_secrets=$(awslocal ecs describe-task-definition \
  --task-definition "$task_definition_arn" \
  --query 'taskDefinition.containerDefinitions[0].secrets' \
  --output json)

jq -e '
  any(.[]; .name == "DJANGO_DB_PASSWORD" and (.valueFrom | endswith(":password::"))) and
  any(.[]; .name == "DJANGO_REDIS_PASSWORD" and (.valueFrom | contains(":secretsmanager:"))) and
  any(.[]; .name == "DJANGO_SECRET_KEY" and (.valueFrom | contains(":secretsmanager:")))
' <<<"$ecs_secrets" >/dev/null || fail "ECS task definition does not use the expected Secrets Manager valueFrom references"

policy_arn=$(tflocal -chdir="$fixture_dir" output -raw execution_policy_arn)
policy_version=$(awslocal iam get-policy \
  --policy-arn "$policy_arn" \
  --query 'Policy.DefaultVersionId' \
  --output text)
policy_document=$(awslocal iam get-policy-version \
  --policy-arn "$policy_arn" \
  --version-id "$policy_version" \
  --query 'PolicyVersion.Document' \
  --output json)
expected_secret_arns=$(tflocal -chdir="$fixture_dir" output -json secretsmanager_secret_arns)
kms_key_arn=$(tflocal -chdir="$fixture_dir" output -raw kms_key_arn)

jq -e --argjson expected "$expected_secret_arns" '
  [.Statement[] |
    select((.Action | if type == "array" then . else [.] end) | index("secretsmanager:GetSecretValue")) |
    .Resource | if type == "array" then . else [.] end][0] | sort == ($expected | sort)
' <<<"$policy_document" >/dev/null || fail "IAM GetSecretValue resources are not the passed bare secret ARNs"

jq -e --arg kms "$kms_key_arn" '
  any(.Statement[];
    ((.Action | if type == "array" then . else [.] end) | index("kms:Decrypt")) and
    .Resource == $kms)
' <<<"$policy_document" >/dev/null || fail "IAM policy does not grant kms:Decrypt on the fixture KMS key"

echo "LocalStack prepare-to-complete runtime-secrets migration passed."
