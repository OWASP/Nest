#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_LIVE_DIR="$(cd "$SCRIPT_DIR/../live" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"

ENV_FILE="$SCRIPT_DIR/../.env"

if [[ -f "$ENV_FILE" ]]; then
    set -a && source "$ENV_FILE" && set +a
fi

if ! curl -sf "http://localhost.localstack.cloud:4566/_localstack/health" >/dev/null 2>&1; then
    echo "ERROR: LocalStack is not running or not ready." >&2
    echo "Start it in another terminal with: make start-localstack" >&2
    exit 1
fi

for cmd in tflocal awslocal docker; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: '$cmd' not found. See infrastructure/README.md prerequisites." >&2
        exit 1
    fi
done

GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || true)
TIMESTAMP=$(date +%Y%m%d%H%M%S)

if [[ -n "$GIT_SHA" ]]; then
    TAG="${GIT_SHA}-${TIMESTAMP}"
else
    TAG="${TIMESTAMP}"
fi

echo "Using image tag: $TAG"

DJANGO_CONFIGURATION="${DJANGO_CONFIGURATION:-Local}"
DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-settings.local}"
DOMAIN_NAME="${DOMAIN_NAME:-localhost}"
ENABLE_CRON_TASKS="${ENABLE_CRON_TASKS:-false}"
DB_PASSWORD="${DB_PASSWORD:-nest_local_db_password}"

TFVARS=$(mktemp)
trap 'rm -f "$TFVARS"' EXIT

cat > "$TFVARS" << EOF
environment           = "local"
backend_image_tag     = "$TAG"
frontend_image_tag    = "$TAG"
django_configuration  = "$DJANGO_CONFIGURATION"
django_settings_module = "$DJANGO_SETTINGS_MODULE"
domain_name           = "$DOMAIN_NAME"
enable_cron_tasks     = $ENABLE_CRON_TASKS
db_password           = "$DB_PASSWORD"
db_deletion_protection = false
db_skip_final_snapshot = true
enable_nat_gateway    = false
EOF

cd "$INFRA_LIVE_DIR"

echo "Initializing Terraform with tflocal..."
tflocal init

echo "Applying Terraform..."
tflocal apply -auto-approve -var-file="$TFVARS"

echo "Retrieving ECR repository URLs..."
BACKEND_ECR=$(tflocal output -raw backend_ecr_repository_url)
FRONTEND_ECR=$(tflocal output -raw frontend_ecr_repository_url)

REGISTRY="$(echo "$BACKEND_ECR" | cut -d/ -f1)"
echo "Logging into local ECR at $REGISTRY..."
awslocal ecr get-login-password | docker login --username AWS --password-stdin "$REGISTRY"

echo "Building backend image..."
docker build \
    -f "$REPO_ROOT/docker/backend/Dockerfile" \
    -t "$BACKEND_ECR:$TAG" \
    "$REPO_ROOT"

echo "Pushing backend image to local ECR..."
docker push "$BACKEND_ECR:$TAG"

FRONTEND_ENV_FILE="frontend/.env"
if [[ ! -f "$REPO_ROOT/$FRONTEND_ENV_FILE" ]]; then
    echo "WARNING: $FRONTEND_ENV_FILE not found, using frontend/.env.example." >&2
    FRONTEND_ENV_FILE="frontend/.env.example"
fi

echo "Building frontend image..."
docker build \
    -f "$REPO_ROOT/docker/frontend/Dockerfile" \
    --build-arg "ENV_FILE=$FRONTEND_ENV_FILE" \
    -t "$FRONTEND_ECR:$TAG" \
    "$REPO_ROOT"

echo "Pushing frontend image to local ECR..."
docker push "$FRONTEND_ECR:$TAG"

echo "Provisioning complete."
echo "  Tag:              $TAG"
echo "  Backend ECR:      $BACKEND_ECR:$TAG"
echo "  Frontend ECR:     $FRONTEND_ECR:$TAG"
echo "  Django config:    $DJANGO_CONFIGURATION"
echo "  Domain:           $DOMAIN_NAME"
