#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: $0 <account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>" >&2
  exit 1
}

[[ $# -eq 1 ]] || usage

image=$1

if [[ ! "$image" =~ ^([0-9]{12})\.dkr\.ecr\.([a-z0-9-]+)\.amazonaws\.com/ ]]; then
  echo "::error::Invalid ECR image reference: ${image}" >&2
  exit 1
fi

registry_id="${BASH_REMATCH[1]}"
region="${BASH_REMATCH[2]}"
registry_prefix="${registry_id}.dkr.ecr.${region}.amazonaws.com/"

repo="${image%:*}"
tag="${image##*:}"

if [[ "$repo" == "$image" || -z "$tag" ]]; then
  echo "::error::Invalid ECR image reference: ${image}" >&2
  exit 1
fi

if [[ "$repo" != "${registry_prefix}"* ]]; then
  echo "::error::Invalid ECR image reference: ${image}" >&2
  exit 1
fi

repo_name="${repo#"$registry_prefix"}"

if [[ -z "$repo_name" ]]; then
  echo "::error::Invalid ECR image reference: ${image}" >&2
  exit 1
fi

digest=$(
  aws ecr batch-get-image \
    --registry-id "$registry_id" \
    --region "$region" \
    --repository-name "$repo_name" \
    --image-ids "imageTag=${tag}" \
    --query 'images[0].imageId.imageDigest' \
    --output text
)

if [[ -z "$digest" || "$digest" == "None" ]]; then
  echo "::error::Image not found in ECR: ${image} (repository: ${repo_name}, tag: ${tag})" >&2
  exit 1
fi

echo "$digest"
