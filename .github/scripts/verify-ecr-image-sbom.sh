#!/usr/bin/env bash

set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

usage() {
  echo "Usage: $0 verify <account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>" >&2
  exit 1
}

[[ $# -eq 2 ]] || usage
[[ "$1" == "verify" ]] || usage

image=$2
repo="${image%:*}"

if [[ "$repo" == "$image" ]]; then
  echo "::error::Invalid ECR image reference: ${image}" >&2
  exit 1
fi

digest=$(bash "$script_dir/ecr-image-digest.sh" "$image")
image_by_digest="${repo}@${digest}"

echo "Verifying SBOM attestation for: ${image_by_digest}"

sbom_spdx=$(
  docker buildx imagetools inspect "$image_by_digest" --format '{{ json .SBOM.SPDX }}' 2>/dev/null || true
)

if [[ -z "$sbom_spdx" || "$sbom_spdx" == "null" ]]; then
  sbom_spdx=$(
    docker buildx imagetools inspect "$image_by_digest" --format '{{ json .SBOM }}' | jq -c '
      if type == "object" then
        [to_entries[] | .value.SPDX // empty] | first // empty
      else
        empty
      end
    ' 2>/dev/null || true
  )
fi

if [[ -z "$sbom_spdx" || "$sbom_spdx" == "null" ]]; then
  echo "::error::No SBOM attestation found for image: ${image_by_digest}" >&2
  exit 1
fi

package_count=$(echo "$sbom_spdx" | jq -r '(.packages // []) | length')

if [[ "$package_count" -eq 0 ]]; then
  echo "::error::SBOM attestation contains no packages for image: ${image_by_digest}" >&2
  exit 1
fi

echo "SBOM attestation verified (${package_count} packages)"
