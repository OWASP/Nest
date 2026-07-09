#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_FILE="$INFRA_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
    set -a && source "$ENV_FILE" && set +a
fi

AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-2}"
SSM_PREFIX="/nest/${ENVIRONMENT:-local}"

if ! command -v awslocal >/dev/null 2>&1; then
    echo "ERROR: 'awslocal' not found. See infrastructure/README.md prerequisites." >&2
    exit 1
fi

put_param() {
    local name="$1"
    local value="$2"
    local type="${3:-String}"

    echo "  OVERWRITE: $SSM_PREFIX/$name = $value"
    AWS_PAGER="" awslocal ssm put-parameter \
        --region "$AWS_DEFAULT_REGION" \
        --name "$SSM_PREFIX/$name" \
        --value "$value" \
        --type "$type" \
        --overwrite \
        --output text >/dev/null
}

echo "Fixing SSM parameters for LocalStack compatibility..."
echo ""

put_param "DJANGO_REDIS_USE_TLS" "false"
put_param "DJANGO_ALLOWED_HOSTS" "localhost,nest-local-alb.elb.localhost.localstack.cloud"

echo ""
echo "Done. Fixed SSM parameters for LocalStack."
