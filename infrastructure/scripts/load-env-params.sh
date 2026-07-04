#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_FILE="$INFRA_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
    set -a && source "$ENV_FILE" && set +a
fi

AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-2}"
SSM_PREFIX="/nest/${ENVIRONMENT:-local}"

DRY_RUN=false
OVERWRITE=false
INCLUDE_EMPTY=false
PARAMETER_COUNT=0
SKIPPED_COUNT=0

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Upload local .env variables from backend/.env and frontend/.env
to LocalStack SSM Parameter Store under $SSM_PREFIX/

Options:
  -n, --dry-run      Print what would be done without actually uploading
  -o, --overwrite    Overwrite existing parameters
  -e, --include-empty   Include variables with empty values
  -h, --help         Show this help message
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--dry-run) DRY_RUN=true; shift ;;
        -o|--overwrite) OVERWRITE=true; shift ;;
        -e|--include-empty) INCLUDE_EMPTY=true; shift ;;
        -h|--help) usage ;;
        *) echo "ERROR: Unknown option: $1" >&2; usage ;;
    esac
done

if ! command -v awslocal >/dev/null 2>&1; then
    echo "ERROR: 'awslocal' not found. See infrastructure/README.md prerequisites." >&2
    exit 1
fi

is_secret() {
    local key="$1"
    local upper
    upper=$(echo "$key" | tr '[:lower:]' '[:upper:]')
    case "$upper" in
        *SECRET*|*PASSWORD*|*TOKEN*|*KEY*|*DSN*) return 0 ;;
        *) return 1 ;;
    esac
}

ENV_FILES=(
    "$REPO_ROOT/backend/.env"
    "$REPO_ROOT/frontend/.env"
)

for env_file in "${ENV_FILES[@]}"; do
    if [[ ! -f "$env_file" ]]; then
        echo "WARNING: $env_file not found, skipping." >&2
        continue
    fi

    echo ""
    echo "Reading: $env_file"

    while IFS='=' read -r key value || [[ -n "$key" ]]; do
        key="$(echo "$key" | tr -d ' ')"
        [[ -z "$key" || "$key" =~ ^# ]] && continue

        value="${value%\"}"
        value="${value#\"}"

        if [[ -z "$value" && "$INCLUDE_EMPTY" == false ]]; then
            echo "  SKIP: $key (empty value, use --include-empty to override)"
            ((SKIPPED_COUNT++)) || true
            continue
        fi

        PARAM_NAME="$SSM_PREFIX/$key"

        if is_secret "$key"; then
            PARAM_TYPE="SecureString"
        else
            PARAM_TYPE="String"
        fi

        if [[ "$DRY_RUN" == true ]]; then
            if [[ "$PARAM_TYPE" == "SecureString" ]]; then
                display="***"
            else
                display="${value:0:40}"
                if [[ ${#value} -gt 40 ]]; then
                    display="${display}..."
                fi
            fi
            
            echo "  WOULD PUT: $PARAM_NAME ($PARAM_TYPE) = $display"
            ((PARAMETER_COUNT++)) || true
            continue
        fi

        if ! AWS_PAGER="" awslocal ssm put-parameter \
            --region "$AWS_DEFAULT_REGION" \
            --name "$PARAM_NAME" \
            --value "$value" \
            --type "$PARAM_TYPE" \
            $([[ "$OVERWRITE" == true ]] && echo "--overwrite") \
            --output text 2>/dev/null; then
            echo "  SKIP: $PARAM_NAME (already exists or error, use --overwrite to force)"
            ((SKIPPED_COUNT++)) || true
            continue
        fi

        echo "  PUT: $PARAM_NAME ($PARAM_TYPE)"
        ((PARAMETER_COUNT++)) || true
    done < "$env_file"
done

echo ""
echo "Done. $PARAMETER_COUNT parameters uploaded, $SKIPPED_COUNT skipped."
