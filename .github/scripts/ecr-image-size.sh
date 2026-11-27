#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: $0 <image-ref> [platform]" >&2
  exit 1
}

[[ $# -ge 1 && $# -le 2 ]] || usage

image=$1
platform=${2:-linux/arm64}
IFS='/' read -r os arch variant _ <<< "${platform}/"

manifest_json=$(docker buildx imagetools inspect "$image" --format '{{json .Manifest}}')

is_index=$(echo "$manifest_json" | jq -r 'if .manifests then "true" else "false" end')

digest=$(
  echo "$manifest_json" | jq -r --arg os "$os" --arg arch "$arch" --arg variant "$variant" '
    if .layers then empty
    else .manifests[]?
      | select(
          .platform.os == $os
          and .platform.architecture == $arch
          and ($variant == "" or .platform.variant == $variant)
        )
      | .digest
    end
  ' | head -1
)

if [[ "$is_index" == "true" ]]; then
  if [[ -z "$digest" ]]; then
    echo "::error::No manifest found for platform ${platform} in image: ${image}" >&2
    exit 1
  fi
  raw_manifest=$(docker buildx imagetools inspect "${image}@${digest}" --raw)
else
  raw_manifest=$(docker buildx imagetools inspect "$image" --raw)
fi

size=$(echo "$raw_manifest" | jq '[.layers[]?.size, .config.size // 0] | add // 0')

if [[ "$size" -eq 0 ]]; then
  echo "::error::Could not determine image size for platform ${platform}: ${image}" >&2
  exit 1
fi

echo "$size"
